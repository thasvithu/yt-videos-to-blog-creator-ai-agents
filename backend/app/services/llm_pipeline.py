"""LangChain + LangGraph pipeline for blog generation."""
from typing import TypedDict, List, Dict, Any
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from app.config import settings


class BlogGenerationState(TypedDict):
    """State for blog generation workflow."""
    video_id: str
    video_title: str
    video_description: str
    channel_title: str
    transcript: str
    metadata: Dict[str, Any]
    key_points: List[str]
    outline: str
    sections: List[Dict[str, str]]
    final_blog: str
    error: str


class LLMPipeline:
    """LangChain + LangGraph pipeline for generating blog posts."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            openai_api_key=settings.openai_api_key
        )
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.openai_api_key
        )
        
        # Prompts
        self.key_points_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert content analyzer. Extract the most important key points from a YouTube video transcript.
Focus on:
- Main topics and themes
- Key insights and takeaways
- Important examples or case studies
- Actionable advice or recommendations

Return a numbered list of 5-10 key points."""),
            ("user", """Video Title: {title}
Channel: {channel}
Description: {description}

Transcript:
{transcript}

Extract the key points:""")
        ])
        
        self.outline_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert blog writer. Create a detailed blog post outline based on video content.
The outline should include:
1. Catchy title (different from video title)
2. Introduction hook
3. Main sections (3-5 sections)
4. Conclusion with call-to-action

Make it engaging and SEO-friendly."""),
            ("user", """Video: {title}
Channel: {channel}

Key Points:
{key_points}

Create a blog outline:""")
        ])
        
        self.section_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert blog writer. Write an engaging blog section based on the outline and key points.
Style guidelines:
- Conversational and engaging tone
- Use subheadings, bullet points, and formatting
- Include examples from the video
- 300-500 words per section
- SEO optimized

Use Markdown formatting."""),
            ("user", """Section to write: {section_title}

Context from video:
{context}

Key points to cover:
{key_points}

Write the section:""")
        ])
        
        self.polish_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert editor. Polish and finalize a blog post.
Tasks:
- Ensure smooth transitions between sections
- Add compelling introduction and conclusion
- Optimize for readability
- Add relevant emojis and formatting
- Ensure SEO optimization

Return the complete, polished blog post in Markdown."""),
            ("user", """Title: {title}

Blog Draft:
{draft}

Polish and finalize:""")
        ])
        
        # Chains
        self.key_points_chain = self.key_points_prompt | self.llm | StrOutputParser()
        self.outline_chain = self.outline_prompt | self.llm | StrOutputParser()
        self.section_chain = self.section_prompt | self.llm | StrOutputParser()
        self.polish_chain = self.polish_prompt | self.llm | StrOutputParser()
    
    def extract_key_points(self, state: BlogGenerationState) -> BlogGenerationState:
        """Extract key points from transcript."""
        try:
            key_points_text = self.key_points_chain.invoke({
                "title": state["video_title"],
                "channel": state["channel_title"],
                "description": state["video_description"],
                "transcript": state["transcript"][:15000]  # Limit for token management
            })
            
            # Parse into list
            key_points = [
                line.strip() for line in key_points_text.split('\n') 
                if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith('-'))
            ]
            
            state["key_points"] = key_points
            return state
        except Exception as e:
            state["error"] = f"Key points extraction failed: {str(e)}"
            return state
    
    def generate_outline(self, state: BlogGenerationState) -> BlogGenerationState:
        """Generate blog outline."""
        try:
            outline = self.outline_chain.invoke({
                "title": state["video_title"],
                "channel": state["channel_title"],
                "key_points": "\n".join(state["key_points"])
            })
            
            state["outline"] = outline
            return state
        except Exception as e:
            state["error"] = f"Outline generation failed: {str(e)}"
            return state
    
    def write_sections(self, state: BlogGenerationState) -> BlogGenerationState:
        """Write individual blog sections."""
        try:
            sections = []
            
            # Parse outline to extract section titles
            outline_lines = state["outline"].split('\n')
            section_titles = [
                line.strip('# ').strip()
                for line in outline_lines
                if line.startswith('##') or line.startswith('###')
            ]
            
            # Write each section
            for section_title in section_titles[:6]:  # Limit to 6 sections
                section_content = self.section_chain.invoke({
                    "section_title": section_title,
                    "context": state["transcript"][:10000],
                    "key_points": "\n".join(state["key_points"])
                })
                
                sections.append({
                    "title": section_title,
                    "content": section_content
                })
            
            state["sections"] = sections
            return state
        except Exception as e:
            state["error"] = f"Section writing failed: {str(e)}"
            return state
    
    def assemble_and_polish(self, state: BlogGenerationState) -> BlogGenerationState:
        """Assemble sections and polish the final blog."""
        try:
            # Assemble draft
            draft_parts = []
            for section in state["sections"]:
                draft_parts.append(f"## {section['title']}\n\n{section['content']}\n")
            
            draft = "\n".join(draft_parts)
            
            # Polish
            final_blog = self.polish_chain.invoke({
                "title": state["video_title"],
                "draft": draft
            })
            
            state["final_blog"] = final_blog
            return state
        except Exception as e:
            state["error"] = f"Assembly/polish failed: {str(e)}"
            return state
    
    def should_continue(self, state: BlogGenerationState) -> str:
        """Check if pipeline should continue or stop."""
        if state.get("error"):
            return "error"
        return "continue"
    
    def build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(BlogGenerationState)
        
        # Add nodes
        workflow.add_node("extract_key_points", self.extract_key_points)
        workflow.add_node("generate_outline", self.generate_outline)
        workflow.add_node("write_sections", self.write_sections)
        workflow.add_node("assemble_polish", self.assemble_and_polish)
        
        # Add edges
        workflow.set_entry_point("extract_key_points")
        workflow.add_edge("extract_key_points", "generate_outline")
        workflow.add_edge("generate_outline", "write_sections")
        workflow.add_edge("write_sections", "assemble_polish")
        workflow.add_edge("assemble_polish", END)
        
        return workflow.compile()
    
    async def generate_blog(
        self,
        video_id: str,
        video_title: str,
        video_description: str,
        channel_title: str,
        transcript: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate blog post from video data.
        
        Returns:
            Dict with 'content' (blog markdown) and 'metadata'
        """
        graph = self.build_graph()
        
        initial_state: BlogGenerationState = {
            "video_id": video_id,
            "video_title": video_title,
            "video_description": video_description,
            "channel_title": channel_title,
            "transcript": transcript,
            "metadata": metadata,
            "key_points": [],
            "outline": "",
            "sections": [],
            "final_blog": "",
            "error": ""
        }
        
        # Run the graph
        final_state = await graph.ainvoke(initial_state)
        
        if final_state.get("error"):
            raise Exception(final_state["error"])
        
        return {
            "content": final_state["final_blog"],
            "metadata": {
                "video_id": video_id,
                "video_title": video_title,
                "channel_title": channel_title,
                "key_points": final_state["key_points"],
                "sections_count": len(final_state["sections"])
            }
        }
