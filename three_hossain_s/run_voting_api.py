from voting_api import app

if __name__ == '__main__':
    print('Starting Voting API on http://0.0.0.0:8000')
    app.run(host='0.0.0.0', port=8000, debug=True)


