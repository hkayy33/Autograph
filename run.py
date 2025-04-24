from WebApp.app import app

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run the Autograph Flask application')
    parser.add_argument('--port', type=int, default=5001, help='Port to run the application on')
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port, debug=True) 