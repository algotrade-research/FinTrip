import matplotlib.pyplot as plt

def visualize(x, y, x_label, y_label, title, path, size=(10, 5)):
    fig = plt.figure(figsize=size)
    plt.xticks(rotation=45)
    plt.plot(x, y)

    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.savefig(path)

def visualize_with_index(dates, y_p, y_i, title, x_label, y_label, path, size=(10, 5)):
    fig = plt.figure(figsize=size())
    plt.xticks(rotation=45)

    plt.plot(dates, y_p, label="index return")
    plt.plot(dates, y_i, label="portfolio")

    plt.title(title)
    plt.legend()
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.savefig(path)
