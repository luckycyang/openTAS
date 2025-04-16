class App():
    def run(self):
        __import__('pprint').pprint("App is running")


if __name__ == "__main__":
    app = App();
    app.run();
