from flask import Blueprint, render_template, request, jsonify
import os
from langchain.prompts import ChatPromptTemplate
from langchain.graphs import Neo4jGraph
from typing import List, Tuple
import traceback

feature1_bp = Blueprint('feature1', __name__,
                       template_folder='templates',
                       static_folder='static')

# Set environment variables directly
os.environ["OPENAI_API_KEY"] = ""
os.environ["NEO4J_URI"] = ""
os.environ["NEO4J_USERNAME"] = ""
os.environ["NEO4J_PASSWORD"] = ""
# Create Neo4j graph connection
try:
    graph = Neo4jGraph(
        url=os.environ["NEO4J_URI"],
        username=os.environ["NEO4J_USERNAME"],
        password=os.environ["NEO4J_PASSWORD"],
    )
    print("Neo4j connection established.")
except Exception as e:
    print(f"Error connecting to Neo4j: {str(e)}")
    graph = None

# Import OpenAI components
try:
    from langchain.chat_models import ChatOpenAI
    from langchain.chains import LLMChain

    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        request_timeout=30,
        max_retries=2
    )
    print("LLM initialized with OpenAI v1.x compatibility.")
except Exception as e:
    print(f"Error initializing LLM: {str(e)}")
    llm = None

def structured_retriever(question: str) -> str:
    if not graph:
        return ""
    try:
        result = graph.query(
            """MATCH (n)
            WHERE n.id IS NOT NULL AND 
                  ANY(prop IN keys(n) WHERE toLower(toString(n[prop])) CONTAINS toLower($query))
            WITH n LIMIT 5
            OPTIONAL MATCH (n)-[r]->(neighbor)
            WITH n, collect(DISTINCT {direction: 'outgoing', type: type(r), neighbor: neighbor.id}) AS outRels
            OPTIONAL MATCH (n)<-[r]-(neighbor)
            WITH n, outRels, collect(DISTINCT {direction: 'incoming', type: type(r), neighbor: neighbor.id}) AS inRels
            WITH n, outRels + inRels AS rels
            UNWIND rels AS rel
            WITH n, rel
            WHERE rel.neighbor IS NOT NULL
            RETURN 
                CASE rel.direction
                    WHEN 'outgoing' THEN n.id + ' - ' + rel.type + ' -> ' + rel.neighbor
                    WHEN 'incoming' THEN rel.neighbor + ' - ' + rel.type + ' -> ' + n.id
                END AS output
            LIMIT 50""",
            {"query": question.lower()},
        )
        return "\n".join([el['output'] for el in result if 'output' in el and el['output']]) if result else ""
    except Exception as e:
        traceback.print_exc()
        return ""

def unstructured_retriever(question: str) -> str:
    if not graph:
        return ""
    try:
        result = graph.query(
            """MATCH (d:Document) 
            WHERE toLower(d.text) CONTAINS toLower($query) 
            RETURN d.text AS content 
            LIMIT 5""",
            {"query": question.lower()}
        )
        if result:
            return "\n#Document ".join([el['content'] for el in result if 'content' in el and el['content']])

        # Fallback query
        fallback_result = graph.query(
            """MATCH (d) 
            WHERE (d:Document OR d:Content OR d:Article OR d:Information) 
            AND ANY(prop IN keys(d) WHERE toLower(toString(d[prop])) CONTAINS toLower($query))
            RETURN d.text AS content, d.body AS body, d.content AS contentText
            LIMIT 5""",
            {"query": question.lower()}
        )
        texts = []
        for item in fallback_result:
            for key in ['content', 'body', 'contentText']:
                if key in item and item[key]:
                    texts.append(item[key])
                    break
        return "\n#Document ".join(texts) if texts else ""
    except Exception as e:
        traceback.print_exc()
        return ""

def retriever(question: str):
    try:
        structured_data = structured_retriever(question).strip()
        unstructured_data = unstructured_retriever(question).strip()

        # UPDATED: Clean fallback data before forming context
        if not structured_data and not unstructured_data:
            return ""

        return f"Structured data:\n{structured_data}\n\nUnstructured data:\n{unstructured_data}".strip()
    except Exception as e:
        traceback.print_exc()
        return ""

def fallback_answer(question: str) -> str:
    question_lower = question.lower()
    if any(word in question_lower for word in ["grow", "plant", "cultivate"]):
        return "Growing plants in urban settings often requires consideration of space, light, water availability, and soil quality. Container gardening and vertical farming are popular solutions for limited spaces."
    if any(word in question_lower for word in ["water", "irrigation"]):
        return "Water management is crucial. Use rainwater harvesting, drip irrigation, and drought-resistant plants."
    return f"Urban agriculture involves food production in cities. Your question: '{question}' is a good starting point. Could you clarify what you'd like to know more specifically?"

def run_chain(question):
    if not llm:
        return fallback_answer(question)
    try:
        context = retriever(question)

        # UPDATED: Use a better prompt to instruct helpful fallback answers
        template = """You are an expert in urban agriculture.

Use the following context to answer the user's question. If the context is empty or not useful, provide a helpful and relevant answer based on your general knowledge.

Context:
{context}

Question: {question}

Answer:"""

        prompt = ChatPromptTemplate.from_template(template)
        chain = LLMChain(llm=llm, prompt=prompt)

        response = chain.run(context=context or "", question=question)  # UPDATED: Allow empty context
        return response.strip() if response else fallback_answer(question)
    except Exception as e:
        traceback.print_exc()
        return fallback_answer(question)

@feature1_bp.route('/')
def home():
    return render_template('features/feature1/index.html')

@feature1_bp.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        question = data.get('question', '')
        if not question:
            return jsonify({'status': 'error', 'message': 'Question cannot be empty'}), 400
        answer = run_chain(question)
        return jsonify({'status': 'success', 'answer': answer})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'success', 'answer': fallback_answer('urban agriculture')})

@feature1_bp.route('/test-connection', methods=['GET'])
def test_connection():
    results = {'neo4j': False, 'llm': False, 'neo4j_message': '', 'llm_message': ''}
    try:
        if graph and graph.query("RETURN 1 AS test"):
            results['neo4j'] = True
            results['neo4j_message'] = 'Connection successful'
    except Exception as e:
        results['neo4j_message'] = str(e)
    try:
        if llm and llm.predict("Say 'hello'"):
            results['llm'] = True
            results['llm_message'] = 'Connection successful'
    except Exception as e:
        results['llm_message'] = str(e)
    return jsonify(results)

@feature1_bp.route('/node-labels', methods=['GET'])
def get_node_labels():
    try:
        if graph:
            result = graph.query("CALL db.labels()")
            labels = [record.get('label') for record in result if 'label' in record]
            return jsonify({'status': 'success', 'labels': labels})
        return jsonify({'status': 'error', 'message': 'Graph not initialized'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})