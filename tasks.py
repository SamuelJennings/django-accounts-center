from invoke import task


@task
def screenshots(c, which):
    print(f"Generating {which} screenshots...")

    auth = "-a auth.json" if which == "private" else ""
    c.run(f"cd screenshots/{which} && shot-scraper multi shots.yml {auth}")


@task
def screenshots_auth(c):
    c.run("cd screenshots/private && shot-scraper auth http://localhost:8000/account-center/login/ auth.json")
