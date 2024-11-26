import matplotlib.pyplot as plt


def visualize(x, y, x_label, y_label, title, path, size=(15, 10)):
    fig = plt.figure(figsize=size)
    plt.xticks(rotation=45)
    plt.plot(x, y)

    plt.title(title)
    plt.grid(visible=True)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.savefig(path)
    plt.close()


def visualize_with_index(dates, y_p, y_i, title, x_label, y_label, path, size=(15, 10)):
    fig = plt.figure(figsize=size)
    plt.xticks(rotation=45)

    plt.plot(dates, y_p, label="portfolio")
    plt.plot(dates, y_i, label="index")

    plt.title(title)
    plt.grid(visible=True)
    plt.legend()
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.savefig(path)
    plt.close()
