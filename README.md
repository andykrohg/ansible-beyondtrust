## Running Red Hat Ansible with BeyondTrust Password Safe and PowerBroker

1. Install `pbrun`
2. Install `ansible`, `git`, and the `community.general` collection (for pbrun become_method plugin):
```bash
yum install -y ansible git
ansible-galaxy collection install community.general
```

3. Setup and run the test playbook:
```bash
# Clone this repository and cd into it
git clone https://github.com/andykrohg/ansible-beyondtrust.git
cd ansible-beyondtrust

# Password safe API URL
export PS_BASE_URL=

# Authorization key provided by Password Safe Management Team
export PS_AUTH_KEY=

# User that will be logged on audit controls in the Password Safe
export PS_RUN_AS=

# Server name list as it is on Password Safe - comma separated
export PS_HOSTS=

# Server user account that the password will be retrieved from PAM
export PS_HOST_ACCOUNT=

# Ansible host group name
export PS_GROUP_NAME=

# Reason for the request to Password Safe
export PS_REASON=

# Duration of the session token - should be longer than it takes to run
# against ALL hosts
export PS_DURATION_MINUTES=

# Inventory script derived from here: https://github.com/eversonleal/pamansibleinventory/blob/master/hosts
ansible-playbook -i inventory.py main.yml
```