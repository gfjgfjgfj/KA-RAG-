from typing import Any, Dict, Iterator, List, Optional, Sequence, Union, Type, Callable, Literal

import google.generativeai as genai
from google.generativeai import GenerativeModel, GenerationConfig
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.messages import BaseMessage
from langchain_core.outputs import GenerationChunk
from langchain_core.prompt_values import PromptValue
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool


class GeminiModel(LLM):
    llm_Model: GenerativeModel = None
    generation_config: GenerationConfig = None
    def __init__(self, key: str, model_name: str, temperature: float = 0.7, max_output_tokens: int = 5000, *args: Any,
                 **kwargs: Any):
        super().__init__(*args, **kwargs)
        genai.configure(api_key=key)
        self.llm_Model = genai.GenerativeModel(model_name)
        self.generation_config = genai.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=max_output_tokens,
            temperature=temperature
        )
    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> str:

        return self.llm_Model.generate_content(contents=prompt, generation_config=self.generation_config).text
    def _stream(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        response = self.llm_Model.generate_content(contents=prompt, generation_config=self.generation_config,
                                                   stream=True)
        for chunk in response:
            yield chunk

    def countToken(self, text: str) -> int:
        return self.llm_Model.count_tokens(contents=text).total_tokens

    def getLLM(self):
        return self.llm_Model

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            # The model name allows users to specify custom token counting
            # rules in LLM monitoring applications (e.g., in LangSmith users
            # can provide per token pricing for their model and monitor
            # costs for the given LLM.)
            "model_name": "GeminiModel",
        }

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model. Used for logging purposes only."""
        return "GeminiModel"

    def bind_tools(
            self,
            tools: Sequence[Union[Dict[str, Any], Type, Callable, BaseTool]],
            *,
            tool_choice: Optional[
                Union[dict, str, Literal["auto", "none", "required", "any"], bool]
            ] = None,
            strict: Optional[bool] = None,
            **kwargs: Any,
    ) -> Runnable[PromptValue | str | Sequence[BaseMessage | list[str] | tuple[str, str] | str | dict[str, Any]], str]:
        formatted_tools = [
            convert_to_openai_tool(tool, strict=strict) for tool in tools
        ]
        if tool_choice:
            if isinstance(tool_choice, str):
                # tool_choice is a tool/function name
                if tool_choice not in ("auto", "none", "any", "required"):
                    tool_choice = {
                        "type": "function",
                        "function": {"name": tool_choice},
                    }
                # 'any' is not natively supported by OpenAI API.
                # We support 'any' since other models use this instead of 'required'.
                if tool_choice == "any":
                    tool_choice = "required"
            elif isinstance(tool_choice, bool):
                tool_choice = "required"
            elif isinstance(tool_choice, dict):
                tool_names = [
                    formatted_tool["function"]["name"]
                    for formatted_tool in formatted_tools
                ]
                if not any(
                        tool_name == tool_choice["function"]["name"]
                        for tool_name in tool_names
                ):
                    raise ValueError(
                        f"Tool choice {tool_choice} was specified, but the only "
                        f"provided tools were {tool_names}."
                    )
            else:
                raise ValueError(
                    f"Unrecognized tool_choice type. Expected str, bool or dict. "
                    f"Received: {tool_choice}"
                )
            kwargs["tool_choice"] = tool_choice
        return super().bind(tools=formatted_tools, **kwargs)
