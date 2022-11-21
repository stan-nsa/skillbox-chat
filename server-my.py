#  Created by Artem Manchenkov
#  artyom@manchenkoff.me
#
#  Copyright © 2019
#
#  Сервер для обработки сообщений от клиентов
#
#  Ctrl + Alt + L - форматирование кода
#
#

from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, connectionDone
from twisted.protocols.basic import LineOnlyReceiver

#==== Class - ServerProtocol ==============================
class ServerProtocol(LineOnlyReceiver):
    factory: 'Server'
    login: str = None

    #def connectionMade(self):

        # Потенциальный баг для внимательных =)
        #self.factory.clients.append(self)

    def connectionLost(self, reason=connectionDone):
        if self.login is not None:
            self.factory.clients.remove(self)

    def lineReceived(self, line: bytes):
        content = line.decode()

        if self.login is not None:
            content = f"Message from {self.login}: {content}"

            # Записываем сообщение в историю
            self.factory.history.append(content)

            for user in self.factory.clients:
                if user is not self:
                    user.sendLine(content.encode())
        else:
            # login:admin -> admin
            if content.startswith("login:"):
                login = content.replace("login:", "")

                for user in self.factory.clients:
                    if user.login.lower() == login.lower():
                        self.sendLine("This login used!!!".encode())
                        self.transport.loseConnection()
                        return

                self.login = login
                self.factory.clients.append(self)
                self.sendLine(f"Welcome, {login}!".encode())
                self.send_history()
            else:
                self.sendLine("Invalid login".encode())

    def send_history(self):
        count = len(self.factory.history) if len(self.factory.history) < self.factory.history_len else self.factory.history_len
        while count:
            self.sendLine(self.factory.history[-count].encode())
            count -= 1


#==== Class - Server ==============================
class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list
    history: list
    history_len = 10

    def startFactory(self):
        self.clients = []
        self.history = []
        print("Server started")

    def stopFactory(self):
        print("Server closed")



reactor.listenTCP(1234, Server())
reactor.run()
