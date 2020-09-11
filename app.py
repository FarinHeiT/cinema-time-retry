from cinema_time_retry_in import socketio, create_app

app = create_app(debug=True)

if __name__ == "__main__":
    socketio.run(app)