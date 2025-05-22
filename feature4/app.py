from flask import Blueprint, render_template, request, jsonify
import groq
import json

feature4_bp = Blueprint('feature4', __name__,
                       template_folder='templates',
                       static_folder='static')

client = groq.Groq(api_key="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")

@feature4_bp.route('/')
def index():
    return render_template('features/feature4/index.html')

@feature4_bp.route('/search', methods=['POST'])
def search():
    location = request.json.get('location')
    
    prompt = f"""Find 5 plant nurseries near {location}. Return ONLY a JSON array with exactly this format, no other text:
    [
        {{
            "name": "Nursery Name",
            "phone": "Contact Number",
            "address": "Full Address",
            "description": "Brief description"
        }},
        // ... more nurseries
    ]

    Important: Return ONLY the JSON array, no additional text or explanation."""
    
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides information about plant nurseries. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        response = completion.choices[0].message.content.strip()
        
        try:
            response = response.replace('```json', '').replace('```', '').strip()
            nurseries = json.loads(response)
            return jsonify({"success": True, "data": json.dumps(nurseries)})
        except json.JSONDecodeError as e:
            return jsonify({
                "success": False, 
                "error": f"Invalid JSON response from API: {str(e)}",
                "raw_response": response
            })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})