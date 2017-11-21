import docker

def startDockerInstance(command):

    client = docker.from_env()

    print(client.containers.run("ubuntu", command))

