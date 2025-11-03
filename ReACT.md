# ReAct (Reasoning + Acting) Prompting Guide 🤖

A comprehensive guide to understanding and implementing ReAct prompting for building LLM agents that can reason and take actions.

---

## 📚 Table of Contents

- [What is ReAct?](#what-is-react)
- [ReAct vs Chain-of-Thought](#react-vs-chain-of-thought)
- [Key Benefits](#key-benefits)
- [The ReAct Loop](#the-react-loop)
- [When to Use ReAct](#when-to-use-react)
- [Implementation Patterns](#implementation-patterns)
- [Pro Tips](#pro-tips)
- [Best Practices](#best-practices)
- [Common Pitfalls](#common-pitfalls)
- [Complete Examples](#complete-examples)
- [Performance Considerations](#performance-considerations)

---

## 🤔 What is ReAct?

**ReAct (Reasoning + Acting)** is a prompting paradigm that synergizes **reasoning traces** with **task-specific actions**, allowing LLMs to interact with external tools, APIs, and environments while maintaining a clear thought process.

### The Core Idea

Instead of just thinking (CoT) or just acting (tool use), ReAct alternates between:
1. **Thought**: Reasoning about what to do next
2. **Action**: Taking a specific action (API call, search, calculation)
3. **Observation**: Processing the result
4. **Repeat**: Until the task is complete

### Simple Example

```
Question: What's the weather like in the birthplace of the current US president?

Thought 1: I need to find out who the current US president is.
Action 1: search("current US president 2025")
Observation 1: Donald Trump is the current US president.

Thought 2: Now I need to find Donald Trump's birthplace.
Action 2: search("Donald Trump birthplace")
Observation 2: Donald Trump was born in Queens, New York City.

Thought 3: Now I can check the weather in Queens, NYC.
Action 3: weather_api("Queens, New York")
Observation 3: Current weather: 52°F, partly cloudy, 10 mph winds.

Thought 4: I have all the information needed to answer.
Action 4: finish("The weather in Queens, New York (Donald Trump's birthplace) is currently 52°F and partly cloudy with 10 mph winds.")
```

---

## 🔄 ReAct vs Chain-of-Thought

| Aspect | Chain-of-Thought (CoT) | ReAct |
|--------|------------------------|-------|
| **Purpose** | Pure reasoning | Reasoning + Action |
| **External Tools** | ❌ No | ✅ Yes |
| **Use Case** | Math, logic, planning | Research, data retrieval, multi-step tasks |
| **Output** | Thoughts → Answer | Thoughts → Actions → Observations → Answer |
| **Complexity** | Medium | High |
| **Cost** | 2-5x normal | 5-20x normal (multiple API calls) |
| **Real-time Data** | ❌ Can't access | ✅ Can access |
| **Best For** | Internal reasoning | External interaction |

### Visual Comparison

**Chain-of-Thought:**
```
Question → Think → Think → Think → Answer
```

**ReAct:**
```
Question → Think → Act → Observe → Think → Act → Observe → Answer
```

---

## 🎓 Key Benefits

| Without ReAct | With ReAct |
|---------------|------------|
| Limited to training data | Can access real-time information |
| Can't verify facts | Can lookup and verify |
| One-shot reasoning | Iterative problem-solving |
| Hallucination-prone | Grounded in real data |
| Static knowledge | Dynamic knowledge retrieval |
| No environmental interaction | Can manipulate external systems |

### Why ReAct Works

1. **Grounding**: Actions provide real data, reducing hallucinations
2. **Flexibility**: Can adapt strategy based on observations
3. **Transparency**: Clear audit trail of decisions and actions
4. **Capability Extension**: LLM gains abilities beyond text generation
5. **Error Recovery**: Can correct course based on feedback
6. **Composability**: Can chain multiple tools together

---

## 🔁 The ReAct Loop

The ReAct pattern follows a cyclical process:

```
┌─────────────────────────────────────────┐
│  1. THOUGHT (Reasoning)                 │
│  "What should I do next?"               │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  2. ACTION (Tool Use)                   │
│  search(), calculate(), api_call()      │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  3. OBSERVATION (Process Result)        │
│  "I received this information..."       │
└───────────────┬─────────────────────────┘
                │
                ▼
         ┌──────┴──────┐
         │  Complete?  │
         └──────┬──────┘
           Yes  │  No
                │  │
                │  └──────► Back to THOUGHT
                │
                ▼
        ┌───────────────┐
        │  FINAL ANSWER │
        └───────────────┘
```

### Loop Limits

Most implementations limit loops to **3-15 iterations** to prevent:
- Infinite loops
- Excessive API costs
- Timeout issues

---

## ⏰ When to Use ReAct

### ✅ Use ReAct For:

- **Information retrieval** (web search, database queries)
- **Multi-step research** (comparing sources, fact-checking)
- **External system interaction** (APIs, databases, tools)
- **Dynamic decision-making** (strategy changes based on results)
- **Verification tasks** (checking facts, validating data)
- **Complex workflows** (booking, ordering, data processing)
- **Real-time data needs** (weather, stocks, news)
- **Tool orchestration** (combining multiple APIs)

### ❌ Skip ReAct For:

- **Simple queries** answerable from training data
- **Creative writing** without factual requirements
- **Pure logic/math** problems (use CoT instead)
- **Cost-sensitive applications** with simple needs
- **When tools aren't available**
- **Real-time latency requirements** (<1 second)

---

## 🔧 Implementation Patterns

### Pattern 1: Basic ReAct Agent

```python
def basic_react_agent(query: str, max_iterations: int = 10) -> str:
    """
    Simple ReAct implementation with thought-action-observation loop.
    """
    tools = {
        "search": web_search,
        "calculate": calculator,
        "finish": lambda x: x
    }
    
    conversation_history = []
    
    for iteration in range(max_iterations):
        # Generate next thought and action
        prompt = f"""
        Answer this question: {query}
        
        You have access to these tools:
        - search(query): Search the web
        - calculate(expression): Perform calculations
        - finish(answer): Provide final answer
        
        Previous steps:
        {format_history(conversation_history)}
        
        What's your next step?
        Format: 
        Thought: [your reasoning]
        Action: [tool_name](argument)
        """
        
        response = llm_call(prompt)
        thought, action = parse_response(response)
        
        conversation_history.append(f"Thought {iteration + 1}: {thought}")
        conversation_history.append(f"Action {iteration + 1}: {action}")
        
        # Execute action
        if action.startswith("finish"):
            return extract_answer(action)
        
        tool_name, argument = parse_action(action)
        result = tools[tool_name](argument)
        
        observation = f"Observation {iteration + 1}: {result}"
        conversation_history.append(observation)
        
        # Check if we have enough information
        if should_finish(result):
            return result
    
    return "Max iterations reached without answer"
```

---

### Pattern 2: Structured ReAct with JSON

```python
def structured_react_agent(query: str) -> Dict:
    """
    ReAct with structured JSON output for better parsing.
    """
    prompt = f"""
    Question: {query}
    
    Use this exact JSON format for each step:
    {{
        "thought": "What I'm thinking...",
        "action": {{
            "tool": "tool_name",
            "input": "tool_input"
        }},
        "observation": "Will be filled after action",
        "continue": true/false
    }}
    
    Available tools: search, calculate, weather_api, finish
    """
    
    steps = []
    
    while True:
        response = llm_call(prompt + format_history(steps))
        step = json.loads(response)
        
        # Execute action
        result = execute_tool(step["action"]["tool"], 
                             step["action"]["input"])
        step["observation"] = result
        steps.append(step)
        
        if not step["continue"] or step["action"]["tool"] == "finish":
            break
    
    return {
        "steps": steps,
        "final_answer": steps[-1]["action"]["input"]
    }
```

---

### Pattern 3: Self-Ask ReAct

The agent asks itself follow-up questions.

```python
def self_ask_react(query: str) -> str:
    """
    ReAct variant where agent asks intermediate questions.
    """
    prompt = f"""
    Question: {query}
    
    Break this down by asking yourself follow-up questions.
    
    Format:
    Are follow up questions needed here: Yes/No
    Follow up: [question]
    Intermediate answer: [search for answer]
    Follow up: [next question]
    ...
    So the final answer is: [answer]
    """
    
    response = llm_call(prompt)
    
    # Parse and execute intermediate searches
    questions = extract_followup_questions(response)
    for q in questions:
        answer = web_search(q)
        response = response.replace(f"Intermediate answer: {q}", 
                                   f"Intermediate answer: {answer}")
    
    return extract_final_answer(response)
```

---

### Pattern 4: ReWOO (Reasoning WithOut Observation)

Plan all actions upfront, then execute in parallel.

```python
def rewoo_agent(query: str) -> str:
    """
    Plan all actions first, execute in parallel, then reason.
    
    More efficient than sequential ReAct.
    """
    # Step 1: Planning
    plan_prompt = f"""
    Question: {query}
    
    Create a plan of all tools you'll need to use:
    #E1 = search(query1)
    #E2 = calculate(expression, depends_on=#E1)
    #E3 = finish(answer, depends_on=#E2)
    """
    
    plan = llm_call(plan_prompt)
    steps = parse_plan(plan)
    
    # Step 2: Parallel Execution
    results = {}
    for step in topological_sort(steps):
        if has_dependencies_met(step, results):
            results[step.id] = execute_tool(step.tool, 
                                           step.input, 
                                           results)
    
    # Step 3: Final Reasoning
    final_prompt = f"""
    Question: {query}
    
    Here are the results from your plan:
    {format_results(results)}
    
    Now provide the final answer.
    """
    
    return llm_call(final_prompt)
```

---

### Pattern 5: ReAct with Memory

Maintain context across multiple queries.

```python
class ReActAgentWithMemory:
    """
    ReAct agent that remembers previous interactions.
    """
    def __init__(self):
        self.memory = []
        self.tools = {
            "search": web_search,
            "remember": self.store_memory,
            "recall": self.retrieve_memory
        }
    
    def store_memory(self, info: str):
        """Store information for later use."""
        self.memory.append({
            "timestamp": datetime.now(),
            "info": info
        })
        return f"Stored: {info}"
    
    def retrieve_memory(self, query: str):
        """Search through stored memories."""
        relevant = [m for m in self.memory if query in m["info"]]
        return relevant
    
    def solve(self, query: str) -> str:
        """
        Solve query using ReAct with memory access.
        """
        prompt = f"""
        Question: {query}
        
        You have access to:
        - search(query): Web search
        - remember(info): Store information
        - recall(query): Retrieve stored info
        
        Previous context: {self.memory[-5:]}
        
        Use Thought-Action-Observation format.
        """
        
        return self.react_loop(prompt)
```

---

## 💡 Pro Tips

### 1. Limit Iteration Count
```python
MAX_ITERATIONS = 10  # Prevent infinite loops

# Track iterations
for i in range(MAX_ITERATIONS):
    if i == MAX_ITERATIONS - 1:
        return fallback_answer()
```

**Why?** Agents can get stuck in loops, especially with ambiguous tasks.

---

### 2. Provide Clear Tool Descriptions
```python
# ❌ Vague
tools = {
    "search": search_function
}

# ✅ Clear
tools = {
    "search": {
        "function": search_function,
        "description": "Search the web for current information. Input: search query string. Output: text snippets.",
        "examples": ["search('weather in Paris')", "search('latest news AI')"]
    }
}
```

**Why?** Better tool descriptions = better tool selection.

---

### 3. Parse Reliably
```python
def parse_thought_action(response: str) -> Tuple[str, str]:
    """
    Robust parsing of Thought and Action.
    """
    # Try structured format first
    if "Thought:" in response and "Action:" in response:
        thought = extract_between(response, "Thought:", "Action:")
        action = extract_after(response, "Action:")
        return thought.strip(), action.strip()
    
    # Fallback: Use LLM to parse
    parse_prompt = f"""
    Extract the thought and action from this response:
    {response}
    
    Return JSON: {{"thought": "...", "action": "..."}}
    """
    parsed = json.loads(llm_call(parse_prompt))
    return parsed["thought"], parsed["action"]
```

**Why?** LLMs don't always follow format exactly.

---

### 4. Handle Tool Failures Gracefully
```python
def execute_tool_safely(tool_name: str, input: str) -> str:
    """
    Execute tool with error handling.
    """
    try:
        result = tools[tool_name](input)
        return result
    except KeyError:
        return f"Error: Tool '{tool_name}' doesn't exist. Available: {list(tools.keys())}"
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"
```

**Why?** Tools fail (API errors, invalid inputs, etc.). Agent needs to adapt.

---

### 5. Use Temperature Strategically
```python
# For reasoning steps (thoughts)
thought_temperature = 0.3  # Focused reasoning

# For creative problem-solving
exploratory_temperature = 0.7  # More creative approaches

# Dynamic temperature
def get_temperature(iteration: int, max_iterations: int) -> float:
    """Increase temperature if stuck."""
    if iteration > max_iterations * 0.7:
        return 0.8  # Get creative if stuck
    return 0.3  # Stay focused initially
```

**Why?** Different phases need different creativity levels.

---

### 6. Implement Early Stopping
```python
def should_stop_early(observation: str, thought: str) -> bool:
    """
    Detect if we have enough information.
    """
    confidence_phrases = [
        "I now have enough information",
        "This answers the question",
        "No further action needed"
    ]
    
    return any(phrase in thought.lower() for phrase in confidence_phrases)
```

**Why?** Save tokens and time when the answer is found early.

---

### 7. Log Everything
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ReAct")

def react_step(iteration: int, thought: str, action: str, observation: str):
    """Log each ReAct step for debugging."""
    logger.info(f"""
    === Iteration {iteration} ===
    Thought: {thought}
    Action: {action}
    Observation: {observation}
    """)
```

**Why?** ReAct agents are complex. Logging helps debug failures.

---

## ✨ Best Practices

### 1. Start Simple, Add Complexity
```python
# Phase 1: Basic ReAct (1-2 tools)
agent = ReActAgent(tools=["search", "finish"])

# Phase 2: Add more tools as needed
agent.add_tool("calculate", calculator)
agent.add_tool("weather", weather_api)

# Phase 3: Add memory, planning, etc.
agent.enable_memory()
agent.enable_planning()
```

---

### 2. Provide Rich Examples
```python
prompt = f"""
Question: {query}

Example of good ReAct reasoning:
Question: What's the population of the capital of France?

Thought 1: I need to identify the capital of France first.
Action 1: search("capital of France")
Observation 1: The capital of France is Paris.

Thought 2: Now I need to find the population of Paris.
Action 2: search("population of Paris 2025")
Observation 2: Paris has a population of approximately 2.2 million.

Thought 3: I have the answer.
Action 3: finish("The population of Paris, the capital of France, is approximately 2.2 million.")

Now solve: {query}
"""
```

---

### 3. Validate Tool Inputs
```python
def validate_tool_input(tool_name: str, input: str) -> Tuple[bool, str]:
    """
    Validate input before executing tool.
    """
    validators = {
        "search": lambda x: len(x) > 0 and len(x) < 500,
        "calculate": lambda x: all(c in "0123456789+-*/() ." for c in x),
        "weather_api": lambda x: len(x.split(",")) <= 2  # City, Country
    }
    
    if tool_name not in validators:
        return True, ""  # Unknown tool, let it try
    
    is_valid = validators[tool_name](input)
    error_msg = f"Invalid input for {tool_name}: {input}" if not is_valid else ""
    
    return is_valid, error_msg
```

---

### 4. Set Clear Success Criteria
```python
def is_answer_complete(answer: str, original_query: str) -> bool:
    """
    Check if the answer adequately addresses the query.
    """
    prompt = f"""
    Query: {original_query}
    Answer: {answer}
    
    Does this answer fully address the query? Yes/No
    """
    
    response = llm_call(prompt, temperature=0.1)
    return "yes" in response.lower()
```

---

### 5. Use Async for Tool Execution
```python
import asyncio

async def execute_tools_parallel(actions: List[Dict]) -> List[str]:
    """
    Execute multiple independent tools in parallel.
    """
    tasks = [
        asyncio.create_task(tool_async(action["tool"], action["input"]))
        for action in actions
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# Use when actions don't depend on each other
results = asyncio.run(execute_tools_parallel([
    {"tool": "search", "input": "Paris weather"},
    {"tool": "search", "input": "Paris population"}
]))
```

---

### 6. Implement Confidence Scoring
```python
def calculate_confidence(thought: str, observation: str) -> float:
    """
    Estimate confidence in current reasoning.
    """
    # Check for hedging language
    low_confidence_words = ["maybe", "perhaps", "possibly", "unclear", "not sure"]
    high_confidence_words = ["definitely", "clearly", "confirmed", "verified"]
    
    text = (thought + " " + observation).lower()
    
    confidence = 0.5  # Base confidence
    confidence -= 0.1 * sum(1 for word in low_confidence_words if word in text)
    confidence += 0.1 * sum(1 for word in high_confidence_words if word in text)
    
    return max(0.0, min(1.0, confidence))
```

---

## ⚠️ Common Pitfalls

### 1. Infinite Action Loops
```python
# ❌ Problem: Agent keeps searching
Thought 1: I need to find information
Action 1: search("topic")
Observation 1: [some info]

Thought 2: I need more information
Action 2: search("topic")  # Same search!
Observation 2: [same info]

# ✅ Solution: Track previous actions
previous_actions = []

def is_repetitive_action(action: str) -> bool:
    if action in previous_actions[-3:]:  # Last 3 actions
        return True
    return False

if is_repetitive_action(current_action):
    force_different_action()
```

---

### 2. Tool Hallucination
```python
# ❌ Problem: Agent invents non-existent tools
Action: super_smart_search("query")  # This tool doesn't exist!

# ✅ Solution: Strict tool validation
available_tools = ["search", "calculate", "weather"]

def validate_action(action: str) -> Tuple[bool, str]:
    tool_name = extract_tool_name(action)
    if tool_name not in available_tools:
        return False, f"Tool '{tool_name}' not available. Use: {available_tools}"
    return True, ""
```

---

### 3. Poor Observation Handling
```python
# ❌ Problem: Agent ignores observations
Observation: "Error: API rate limit exceeded"
Thought: Let me search again  # Ignores error!

# ✅ Solution: Explicitly check observation
def analyze_observation(observation: str) -> Dict:
    if "error" in observation.lower():
        return {
            "status": "error",
            "should_retry": False,
            "alternate_approach": "Try different tool"
        }
    return {"status": "success"}
```

---

### 4. Overusing Tools
```python
# ❌ Wasteful
Question: What's 2+2?

Thought: I should calculate this
Action: calculate("2+2")
Observation: 4

# ✅ Efficient
Question: What's 2+2?

Thought: This is simple arithmetic
Action: finish("4")

# Rule: Use tools for external data, not for things LLM knows
```

---

### 5. Not Handling Partial Information
```python
# ❌ Problem: Gives up too early
Observation: "Population data from 2020: 2.1M"
Thought: This is outdated, I need 2025 data
Action: search("population 2025")
Observation: "No recent data available"
Thought: I can't answer this  # Gives up!

# ✅ Solution: Use best available data
Thought: 2020 data is recent enough. I'll use it with a caveat.
Action: finish("Approximately 2.1 million as of 2020. More recent data not available.")
```

---

### 6. Forgetting Context
```python
# ❌ Problem: Loses track of goal
Thought 1: Find capital of France
Action 1: search("capital of France")
Observation 1: Paris

Thought 2: Interesting! Let me learn about Paris history
Action 2: search("Paris history")  # Off track!

# ✅ Solution: Reference original query
def generate_thought(query: str, history: List) -> str:
    prompt = f"""
    Original Question: {query}
    
    Previous steps: {history}
    
    Next thought (stay focused on answering the original question):
    """
    return llm_call(prompt)
```

---

## 📖 Complete Examples

### Example 1: Simple Fitness Agent with ReAct

```python
class FitnessReActAgent:
    """
    ReAct agent for fitness queries with tool access.
    """
    def __init__(self):
        self.tools = {
            "search_exercises": self.search_exercises,
            "calculate_calories": self.calculate_calories,
            "check_equipment": self.check_equipment,
            "get_user_profile": self.get_user_profile,
            "finish": lambda x: x
        }
    
    def search_exercises(self, query: str) -> str:
        """Search exercise database."""
        # Mock implementation
        exercises = {
            "chest": "Push-ups, Bench Press, Chest Flyes",
            "legs": "Squats, Lunges, Leg Press",
            "cardio": "Running, Cycling, Jumping Jacks"
        }
        return exercises.get(query.lower(), "No exercises found")
    
    def calculate_calories(self, activity: str) -> str:
        """Estimate calorie burn."""
        calories = {
            "running": "300-400 per 30 min",
            "yoga": "120-180 per 30 min",
            "hiit": "250-350 per 30 min"
        }
        return calories.get(activity.lower(), "Unknown activity")
    
    def solve(self, query: str) -> Dict:
        """
        Solve fitness query using ReAct.
        """
        history = []
        
        for iteration in range(10):
            prompt = f"""
            Question: {query}
            
            Available tools:
            - search_exercises(muscle_group): Find exercises
            - calculate_calories(activity): Estimate calorie burn
            - check_equipment(exercise): Check equipment needs
            - get_user_profile(): Get user fitness level
            - finish(answer): Provide final answer
            
            Previous steps:
            {self._format_history(history)}
            
            Format:
            Thought: [reasoning]
            Action: [tool_name](argument)
            """
            
            response = llm_call(prompt, temperature=0.3)
            thought = self._extract_thought(response)
            action = self._extract_action(response)
            
            history.append(f"Thought {iteration + 1}: {thought}")
            history.append(f"Action {iteration + 1}: {action}")
            
            # Execute action
            if action.startswith("finish"):
                return {
                    "answer": self._extract_argument(action),
                    "reasoning_steps": history
                }
            
            tool_name, argument = self._parse_action(action)
            observation = self.tools[tool_name](argument)
            history.append(f"Observation {iteration + 1}: {observation}")
        
        return {"answer": "Could not complete task", "reasoning_steps": history}

# Usage
agent = FitnessReActAgent()
result = agent.solve("What exercises should I do for chest day at home?")

# Output:
# {
#     "answer": "For chest day at home, focus on: Push-ups (standard and variations), 
#                Chest dips (using chairs), and Resistance band flyes. These require 
#                minimal equipment and effectively target chest muscles.",
#     "reasoning_steps": [
#         "Thought 1: I need to find chest exercises suitable for home",
#         "Action 1: search_exercises(chest)",
#         "Observation 1: Push-ups, Bench Press, Chest Flyes",
#         "Thought 2: I should check which of these work at home",
#         "Action 2: check_equipment(Bench Press)",
#         "Observation 2: Requires: Bench, Barbell",
#         "Thought 3: Bench Press needs equipment. Let me focus on bodyweight",
#         "Action 3: finish([answer])"
#     ]
# }
```

---

### Example 2: Research Assistant

```python
class ResearchReActAgent:
    """
    ReAct agent for research tasks.
    """
    def __init__(self):
        self.tools = {
            "web_search": self.web_search,
            "read_article": self.read_article,
            "fact_check": self.fact_check,
            "compare_sources": self.compare_sources,
            "finish": lambda x: x
        }
        self.findings = []
    
    def research(self, question: str) -> Dict:
        """
        Conduct research using ReAct.
        """
        prompt_template = """
        Research Question: {question}
        
        Your goal: Provide a well-researched answer using multiple sources.
        
        Available tools:
        - web_search(query): Search for information
        - read_article(url): Read full article content
        - fact_check(claim): Verify a claim across sources
        - compare_sources(topic): Compare what multiple sources say
        - finish(answer): Provide final researched answer
        
        Research so far:
        {history}
        
        Guidelines:
        1. Search for multiple sources
        2. Verify important claims
        3. Compare conflicting information
        4. Cite your sources in the final answer
        
        Next step:
        Thought: [what to do next]
        Action: [tool](argument)
        """
        
        history = []
        sources_used = []
        
        for i in range(15):  # More iterations for research
            prompt = prompt_template.format(
                question=question,
                history="\n".join(history[-10:])  # Last 10 steps
            )
            
            response = llm_call(prompt, temperature=0.4)
            thought, action = self._parse_response(response)
            
            history.append(f"Thought {i+1}: {thought}")
            history.append(f"Action {i+1}: {action}")
            
            if "finish" in action:
                return {
                    "answer": self._extract_argument(action),
                    "sources": sources_used,
                    "research_process": history
                }
            
            # Execute tool
            tool_name, arg = self._parse_action(action)
            result = self.tools[tool_name](arg)
            
            if tool_name in ["web_search", "read_article"]:
                sources_used.append(arg)
            
            observation = f"Observation {i+1}: {result}"
            history.append(observation)
            
            # Check for sufficient information
            if len(sources_used) >= 3 and "finish" not in action:
                history.append("Note: You have 3+ sources. Consider finishing soon.")
        
        return {
            "answer": "Research incomplete",
            "sources": sources_used,
            "research_process": history
        }

# Usage
agent = ResearchReActAgent()
result = agent.research("What are the health benefits of intermittent fasting?")
```

---

### Example 3: ReAct for E-commerce

```python
class ShoppingReActAgent:
    """
    ReAct agent for shopping assistance.
    """
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.tools = {
            "search_products": self.search_products,
            "get_product_details": self.get_product_details,
            "check_reviews": self.check_reviews,
            "compare_prices": self.compare_prices,
            "check_inventory": self.check_inventory,
            "get_user_preferences": self.get_user_preferences,
            "add_to_cart": self.add_to_cart,
            "finish": lambda x: x
        }
    
    def shop(self, request: str) -> Dict:
        """
        Help user shop using ReAct reasoning.
        """
        prompt = f"""
        Shopping Request: {request}
        User: {self.user_id}
        
        Tools available:
        - search_products(query): Find products
        - get_product_details(product_id): Get full details
        - check_reviews(product_id): Read customer reviews
        - compare_prices(product_ids): Compare prices across products
        - check_inventory(product_id): Check stock
        - get_user_preferences(): Get user's preferences and history
        - add_to_cart(product_id): Add item to cart
        - finish(message): Complete the task
        
        Steps so far:
        {{history}}
        
        Next step:
        Thought: [reasoning about what to do]
        Action: [tool](argument)
        """
        
        conversation = []
        cart_items = []
        
        for i in range(12):
            current_prompt = prompt.format(history="\n".join(conversation))
            response = llm_call(current_prompt, temperature=0.3)
            
            thought, action = self._parse(response)
            conversation.append(f"Thought: {thought}")
            conversation.append(f"Action: {action}")
            
            if "finish" in action:
                return {
                    "message": self._extract_arg(action),
                    "cart": cart_items,
                    "process": conversation
                }
            
            tool, arg = self._parse_action(action)
            result = self.tools[tool](arg)
            
            if tool == "add_to_cart":
                cart_items.append(arg)
            
            conversation.append(f"Observation: {result}")
        
        return {
            "message": "Shopping session incomplete",
            "cart": cart_items,
            "process": conversation
        }

# Example usage
agent = ShoppingReActAgent(user_id="user123")
result = agent.shop("I need running shoes for marathon training, budget $150")

# Output might be:
# {
#     "message": "I've added the Nike Pegasus 40 to your cart. 
#                 It has excellent reviews for marathon training, 
#                 is within your $150 budget at $130, and is in stock.",
#     "cart": ["nike-pegasus-40-mens-size-10"],
#     "process": [...]
# }
```

---

## ⚡ Performance Considerations

### Latency Comparison

```
Direct Answer:       ████░░░░░░░░░░░░░░░░ (1-2 sec)
Chain-of-Thought:    ████████░░░░░░░░░░░░ (3-5 sec)
ReAct (3 tools):     ████████████████░░░░ (8-15 sec)
ReAct (10 tools):    ████████████████████ (20-40 sec)
```

### Token Usage

```
Task: "Find best laptop under $1000"

Direct (no tools):
Input:  100 tokens
Output: 150 tokens
Total:  250 tokens
Cost:   $0.008

ReAct (5 iterations):
Input:  100 + (300 × 5) = 1,600 tokens  [prompt + context each iteration]
Output: (150 × 5) + 200 = 950 tokens    [thoughts + actions + final]
Total:  2,550 tokens
Cost:   $0.08 (10x more)
```

### Cost Optimization Strategies

```python
# 1. Cache tool results
tool_cache = {}

def execute_tool_cached(tool: str, input: str) -> str:
    cache_key = f"{tool}:{input}"
    if cache_key in tool_cache:
        return tool_cache[cache_key]
    
    result = execute_tool(tool, input)
    tool_cache[cache_key] = result
    return result

# 2. Use cheaper models for observations
def process_observation(observation: str) -> str:
    """Use GPT-3.5 for simple summarization."""
    if len(observation) > 1000:
        summary = cheap_llm_call(f"Summarize: {observation}")
        return summary
    return observation

# 3. Batch API calls
async def execute_parallel_tools(actions: List) -> List:
    """Execute independent tools in parallel."""
    results = await asyncio.gather(*[
        execute_tool_async(a["tool"], a["input"]) 
        for a in actions
    ])
    return results
```

### Success Rates

Based on research and benchmarks:

| Task Type | Success Rate | Avg Iterations |
|-----------|--------------|----------------|
| Simple lookup | 95%+ | 2-3 |
| Multi-step research | 80-90% | 5-8 |
| Complex reasoning | 70-80% | 8-12 |
| Ambiguous tasks | 50-70% | 10+ |

---

## 🎯 Quick Reference

### ReAct vs Alternatives

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **Direct Prompting** | Simple Q&A | Fast, cheap | No tools, hallucination risk |
| **Chain-of-Thought** | Logic problems | Good reasoning | No external data |
| **ReAct** | Research, complex tasks | Tools + reasoning | Slower, expensive |
| **ReWOO** | Known workflow | Parallel execution | Less flexible |
| **Function Calling** | Structured APIs | Clean tool use | Less reasoning |

### When to Use Each Pattern

| Pattern | Use Case | Example |
|---------|----------|---------|
| Basic ReAct | General research | "What's the weather in Paris?" |
| Structured ReAct | Production systems | API integration with logging |
| Self-Ask | Decomposable questions | "Who won the World Cup in the year Taylor Swift was born?" |
| ReWOO | Predictable workflows | "Compare prices, then check inventory, then add to cart" |
| ReAct + Memory | Multi-turn conversations | Customer support chat |

---

## 📚 Further Reading

### Research Papers
- **"ReAct: Synergizing Reasoning and Acting in Language Models"** (Yao et al., 2022)
  - Original ReAct paper
  
- **"ReWOO: Decoupling Reasoning from Observations"** (Xu et al., 2023)
  - More efficient ReAct variant

- **"Toolformer: Language Models Can Teach Themselves to Use Tools"** (Schick et al., 2023)
  - Alternative approach to tool use

- **"Gorilla: Large Language Model Connected with Massive APIs"** (Patil et al., 2023)
  - API-focused tool use

### Frameworks
- **LangChain**: Python framework with ReAct agents
- **LlamaIndex**: Data framework with agent support
- **AutoGPT**: Autonomous agent framework
- **BabyAGI**: Task-driven autonomous agent

### Tools & Libraries
```bash
# LangChain ReAct
pip install langchain

# OpenAI function calling
pip install openai

# Semantic Kernel (Microsoft)
pip install semantic-kernel
```

---

## 🏁 Summary Checklist

Before implementing ReAct:

- [ ] Do I need external tools/APIs?
- [ ] Is reasoning transparency important?
- [ ] Can I afford 5-20x token cost?
- [ ] Do I have 5-30 seconds for latency?
- [ ] Are my tools reliable (error handling)?
- [ ] Have I limited max iterations?
- [ ] Can I parse Thought-Action-Observation format?
- [ ] Do I have fallback logic?
- [ ] Am I logging the reasoning process?
- [ ] Have I tested with edge cases?

### Red Flags (Don't Use ReAct If...)

- ❌ Task is answerable without tools
- ❌ Latency requirements <3 seconds
- ❌ Cost is primary concern
- ❌ Tools are unreliable or slow
- ❌ Simple rule-based logic would suffice

---

## 💬 Common Questions

**Q: Can I combine CoT and ReAct?**
A: Yes! ReAct already uses reasoning (thoughts). You can make thoughts more detailed using CoT techniques.

**Q: What if my tool fails?**
A: Return a clear error message as the observation. The agent should reason about alternatives.

**Q: How many tools is too many?**
A: More than 10-15 tools can confuse the agent. Group related tools or use a tool selector.

**Q: Should every action use a tool?**
A: No! The agent can reason without tools and use `finish()` when ready.

**Q: How do I prevent infinite loops?**
A: Set max iterations, detect repeated actions, implement early stopping.

**Q: Can I use ReAct with GPT-3.5?**
A: Yes, but GPT-4+ performs significantly better at following the ReAct format.

**Q: Is ReAct the same as function calling?**
A: No. Function calling is structured tool use. ReAct adds explicit reasoning between tool calls.

---

## 🚀 Getting Started Template

```python
class MyReActAgent:
    """
    Minimal ReAct agent template.
    """
    def __init__(self):
        self.tools = {
            "tool1": self.tool1_function,
            "tool2": self.tool2_function,
            "finish": lambda x: x
        }
    
    def solve(self, query: str, max_iter: int = 10) -> str:
        history = []
        
        for i in range(max_iter):
            # Build prompt
            prompt = self._build_prompt(query, history)
            
            # Get LLM response
            response = llm_call(prompt)
            
            # Parse thought and action
            thought, action = self._parse(response)
            history.append(f"Thought: {thought}")
            history.append(f"Action: {action}")
            
            # Check if done
            if "finish" in action:
                return self._extract_answer(action)
            
            # Execute tool
            tool, arg = self._parse_action(action)
            result = self.tools[tool](arg)
            history.append(f"Observation: {result}")
        
        return "Max iterations reached"
    
    def _build_prompt(self, query: str, history: List[str]) -> str:
        return f"""
        Question: {query}
        
        Use Thought-Action-Observation format.
        Tools: {list(self.tools.keys())}
        
        {chr(10).join(history)}
        
        Next step:
        """
```

---

**Happy Building! 🤖**

*Last Updated: November 2025*
