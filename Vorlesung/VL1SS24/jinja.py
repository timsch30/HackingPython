import jinja2


def print_mails():
    env = jinja2.Environment()
    temp = env.from_string("Hello, {{name}}\n"
                           "How are you doing?\n"
                           "Greetings, Derk")

    for word in ["Luke", "Anakin", "Padme"]:
        print(temp.render(name=word))


def print_text():
    env = jinja2.Environment()
    temp = env.from_string("{% for text in texts %} {{text}} {% endfor %} \n")

    texts = ["Luke is a Jedi", "Vador is a Darth", "Han is a Warrior"]

    print(temp.render(texts=texts))


print_text()