
if __name__ == '__main__':
    import pywebcopy

    pywebcopy.core.save_webpage('http://localhost:5000', 'e://tests/', copy_all=True, bypass_robots=True,)