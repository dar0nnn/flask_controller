from scales import create_app

config_name = "development"
app = create_app(config_name)

if __name__ == '__main__':
    app.run(host='192.168.1.166', port=5005, threaded=True)