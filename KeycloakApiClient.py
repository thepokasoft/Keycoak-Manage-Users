import csv

from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection


class KeyCloakAPI:
    def __init__(self):
        self.user_id_keycloak = None
        self.password = None
        self.lastname = None
        self.firstname = None
        self.username = None
        self.email = None
        self.keycloak_admin = None
        self.relm_role_name = None
        self.client_role_name = None
        self.client_id = None
        self.group_name = None

    def configure_client(self):
        keycloak_connection = KeycloakOpenIDConnection(
            server_url='',
            username='',
            password='',
            realm_name="",
            user_realm_name="",
            client_id="",
            verify=True)
        self.keycloak_admin = KeycloakAdmin(connection=keycloak_connection)
        self.relm_role_name = ""
        self.client_role_name = ""
        self.client_id = ""
        self.group_name = ""

        count_users = self.keycloak_admin.users_count()
        print("Testing connection string... Number of users in system:" + str(count_users))

    def set_user_details(self, firstname, lastname, email, username, password):
        self.email = email
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.password = password

    def add_user(self):
        self.keycloak_admin.create_user({"email": self.email,
                                         "username": self.username,
                                         "enabled": True,
                                         "firstName": self.firstname,
                                         "lastName": self.lastname,
                                         "credentials": [{"value": self.password, "type": "password", }]})
        print("User Created")
        self.user_id_keycloak = self.keycloak_admin.get_user_id(self.username)
        print("User ID:" + str(self.user_id_keycloak))

    def add_group(self):
        group = self.keycloak_admin.get_group_by_path(path=self.group_name)
        self.keycloak_admin.group_user_add(user_id=self.user_id_keycloak, group_id=group['id'])
        print("group Added")

    def add_client_role(self):
        clients = self.keycloak_admin.get_clients()
        client_id_uuid = ""
        for client in clients:
            if self.client_id == client.get("clientId"):
                client_id_uuid = client["id"]
        client_role = self.keycloak_admin.get_client_role(client_id=client_id_uuid, role_name=self.client_role_name)
        self.keycloak_admin.assign_client_role(client_id=client_id_uuid, user_id=self.user_id_keycloak, roles=[client_role])
        print("Client Role Assigned")

    def add_relm_role(self):
        realm_role = self.keycloak_admin.get_realm_role(role_name=self.relm_role_name)
        self.keycloak_admin.assign_realm_roles(user_id=self.user_id_keycloak, roles=[realm_role])
        print("realm_role Assigned")


if __name__ == '__main__':
    keyCloakApi = KeyCloakAPI()
    keyCloakApi.configure_client()

    with open('./file.csv') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            name = row[0]
            email = row[1]
            username = row[2]
            password = row[3]
            firstname = name[:name.lower().find(username[1:].lower())].strip()
            lastname = name[len(firstname):].strip()
            print([firstname, lastname, username, email, password])
            keyCloakApi.set_user_details(firstname, lastname, email, username, password)
            keyCloakApi.add_user()
            keyCloakApi.add_relm_role()
            keyCloakApi.add_client_role()
            keyCloakApi.add_group()
