"""
Web Server for Test Case Generator - Clean Backend

This Flask application provides a clean REST API backend.
All frontend code (HTML/CSS/JS) is separated into templates and static files.

Project Structure:
    web_server.py           - Flask backend (this file)
    templates/index.html    - HTML structure
    static/css/style.css    - CSS styling
    static/js/app.js        - JavaScript logic

Usage:
    python web_server.py
    Then open http://localhost:8000 in your browser
"""

from flask import Flask, request, jsonify, render_template, Response
from pathlib import Path
from datetime import datetime
import json
import queue
import traceback

# Import configuration if available
try:
    import config
    DEFAULT_MODEL = config.MODEL_NAME
except ImportError:
    DEFAULT_MODEL = "llama3.2-vision:11b"

# Import test case generator modules with fallback
try:
    from test_case_generator import TestCaseGenerator, FileOperations
except ImportError:
    try:
        from src.test_case_generator import TestCaseGenerator, FileOperations
    except ImportError:
        print("ERROR: Cannot import test_case_generator module.")
        print("Please run: pip install -e .")
        exit(1)

# Initialize Flask app
app = Flask(__name__)

# Configuration
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Log queue management for real-time streaming
log_queues = {}


def add_log(session_id, message, level="info"):
    """
    Add a log message to the queue for a specific session.

    Args:
        session_id: Unique identifier for the generation session
        message: Log message to add
        level: Log level (info, success, warning, error)
    """
    if session_id in log_queues:
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_queues[session_id].put({
            "timestamp": timestamp,
            "level": level,
            "message": message
        })


# ============================================================================
# ROUTES - Frontend
# ============================================================================

@app.route('/')
def index():
    """
    Serve the main application page.

    Returns:
        Rendered HTML template with configuration
    """
    return render_template('index.html', model_name=DEFAULT_MODEL)


# ============================================================================
# ROUTES - API Endpoints
# ============================================================================

@app.route('/api/generate', methods=['POST'])
def generate_test_cases():
    """
    Generate test cases from user story and acceptance criteria.

    Expected JSON payload:
        {
            "user_story": "As a user...",
            "acceptance_criteria": ["criterion 1", "criterion 2"],
            "filename": "test_cases",
            "append_datetime": true,
            "session_id": "session_123456"
        }

    Returns:
        JSON response with success status, file path, and test case count
    """
    session_id = None

    try:
        # Parse request data
        data = request.json
        user_story = data.get('user_story', '').strip()
        acceptance_criteria = data.get('acceptance_criteria', [])
        filename = data.get('filename', 'test_cases').strip()
        append_datetime = data.get('append_datetime', True)
        session_id = data.get('session_id')

        # Validate inputs
        if not user_story:
            add_log(session_id, "Validation failed: No user story provided", "error")
            return jsonify({'error': 'User story is required'}), 400

        if not acceptance_criteria or len(acceptance_criteria) == 0:
            add_log(session_id, "Validation failed: No acceptance criteria provided", "error")
            return jsonify({'error': 'At least one acceptance criterion is required'}), 400

        # Log validation success
        add_log(session_id, "Input validation passed", "success")
        add_log(session_id, f"User story: {user_story[:50]}...", "info")
        add_log(session_id, f"Processing {len(acceptance_criteria)} acceptance criteria", "info")

        # Prepare filename
        filename = Path(filename).stem
        if append_datetime:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{filename}_{timestamp}"
        filename = f"{filename}.csv"
        output_path = OUTPUT_DIR / filename

        add_log(session_id, f"Output file: {filename}", "info")

        # Initialize generator
        add_log(session_id, f"Initializing AI model: {DEFAULT_MODEL}", "info")
        generator = TestCaseGenerator(
            model_name=DEFAULT_MODEL,
            include_edge_cases=True,
            include_negative_tests=True
        )
        add_log(session_id, "AI model initialized successfully", "success")

        # Generate test cases
        add_log(session_id, "Starting test case generation...", "warning")
        add_log(session_id, "This may take 30-60 seconds depending on complexity", "warning")

        test_cases = generator.generate_test_cases_with_retry(
            user_story=user_story,
            acceptance_criteria=acceptance_criteria,
            max_retries=5
        )

        add_log(session_id, f"AI generated {len(test_cases)} test cases", "success")

        # Validate test cases
        add_log(session_id, "Validating generated test cases...", "info")
        # Validation is done within generator, so if we get here it's valid
        add_log(session_id, "Validation passed ✓", "success")

        # Save to file
        add_log(session_id, f"Saving test cases to: {output_path}", "info")
        FileOperations.save_test_cases_csv(
            test_cases=test_cases,
            filepath=str(output_path),
            preserve_line_breaks=True,
            include_summary=True
        )
        add_log(session_id, "File saved successfully ✓", "success")
        add_log(session_id, "Generation complete! 🎉", "success")

        # Return success response
        return jsonify({
            'success': True,
            'file_path': str(output_path),
            'test_case_count': len(test_cases),
            'message': f'Successfully generated {len(test_cases)} test cases'
        }), 200

    except ConnectionError as e:
        error_msg = f"Cannot connect to Ollama. Ensure Ollama is running with {DEFAULT_MODEL} model."
        add_log(session_id, f"Connection error: {str(e)}", "error")
        return jsonify({'error': error_msg, 'details': str(e)}), 503

    except ValueError as e:
        add_log(session_id, f"Generation error: {str(e)}", "error")
        return jsonify({'error': 'Failed to generate valid test cases', 'details': str(e)}), 500

    except Exception as e:
        add_log(session_id, f"Unexpected error: {str(e)}", "error")
        print(f"Error during generation: {e}")
        print(traceback.format_exc())
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500


@app.route('/api/logs/<session_id>')
def stream_logs(session_id):
    """
    Stream logs to client using Server-Sent Events (SSE).

    Args:
        session_id: Unique identifier for the generation session

    Returns:
        SSE stream of log messages
    """
    def generate():
        # Create queue for this session
        log_queues[session_id] = queue.Queue()

        try:
            while True:
                try:
                    # Get log message from queue (with timeout)
                    log_entry = log_queues[session_id].get(timeout=30)
                    yield f"data: {json.dumps(log_entry)}\n\n"
                except queue.Empty:
                    # Send keepalive to prevent timeout
                    yield f": keepalive\n\n"
        finally:
            # Cleanup queue when connection closes
            if session_id in log_queues:
                del log_queues[session_id]

    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/health')
def health_check():
    """
    Health check endpoint to verify server and Ollama status.

    Returns:
        JSON with health status and model information
    """
    try:
        import ollama
        ollama.list()

        return jsonify({
            'status': 'healthy',
            'ollama': 'connected',
            'model': DEFAULT_MODEL,
            'output_dir': str(OUTPUT_DIR.absolute())
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'ollama': 'disconnected',
            'error': str(e)
        }), 503


@app.route('/api/config')
def get_config():
    """
    Get current configuration.

    Returns:
        JSON with current configuration settings
    """
    return jsonify({
        'model': DEFAULT_MODEL,
        'output_directory': str(OUTPUT_DIR.absolute())
    }), 200


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("Test Case Generator - Web Server")
    print("=" * 70)
    print(f"Model: {DEFAULT_MODEL}")
    print(f"Output Directory: {OUTPUT_DIR.absolute()}")
    print("\n✨ Features:")
    print("  • Single-field paste input")
    print("  • Real-time log streaming")
    print("  • Clean REST API backend")
    print("  • Separated HTML/CSS/JS frontend")
    print("\nServer starting...")
    print("\n👉 Open your browser: http://localhost:8000")
    print("\n💡 API Endpoints:")
    print("  POST /api/generate      - Generate test cases")
    print("  GET  /api/logs/<id>     - Stream logs (SSE)")
    print("  GET  /api/health        - Health check")
    print("  GET  /api/config        - Get configuration")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 70)

    # Run the Flask application
    app.run(
        debug=True,
        host='0.0.0.0',
        port=8000,
        threaded=True
    )