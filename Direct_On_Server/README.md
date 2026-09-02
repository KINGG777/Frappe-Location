# Frappe Helpdesk v16 — Direct Server Deployment & Location Customization

Complete deployment guide for Frappe Helpdesk v16 on Ubuntu using a direct server installation.

> Deployment Type: Direct Ubuntu Installation  
> Frappe Bench: `/var/www/Frappe`  
> Customization Source: `/var/www/Frappe-Location`  
> Site: `pkdevops.online`  
> Web Server: Apache  
> Process Manager: Supervisor  
> Database: MariaDB  
> Cache/Queue: Redis  
> Python: 3.14  
> Node.js: 24

---

## 1. System Update

    sudo apt-get update && sudo apt-get upgrade -y
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update

---

## 2. Install Apache

    sudo apt install apache2 -y

    sudo systemctl enable apache2
    sudo systemctl start apache2

    sudo systemctl status apache2

---

## 3. Install Python 3.14

    sudo apt install python3.14 python3.14-venv -y

    python3.14 -m ensurepip --upgrade

    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc

    pip3.14 --version

    python3.14 -m pip install --upgrade pip

    sudo apt-get install python3-setuptools python3-pip -y

    sudo apt install pkg-config -y

    sudo apt install python3.14-dev -y

---

## 4. Install MariaDB

    sudo apt install mariadb-server -y

    sudo mysql_secure_installation

    sudo apt-get install libmysqlclient-dev -y

    sudo systemctl enable mariadb
    sudo systemctl start mariadb

    sudo systemctl status mariadb

---

## 5. Install Redis

    sudo apt-get install redis-server -y

    sudo systemctl enable redis-server
    sudo systemctl start redis-server

    sudo systemctl status redis-server

---

## 6. Install Node.js and Yarn

### Install curl

    sudo apt install curl -y

### Install NVM

    curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
    source ~/.profile

### Install npm

    sudo apt-get install npm -y

### Install Yarn

    sudo npm install -g yarn

### Install Node.js 24

    nvm install 24
    nvm use 24

### Verify

    node -v
    npm -v
    yarn -v

Expected Node.js:

    v24.x.x

---

## 7. Install wkhtmltopdf

Install required packages:

    sudo apt-get install xvfb libfontconfig fontconfig -y
    sudo apt-get install xfonts-75dpi -y

Check architecture:

    uname -m

For an x86_64 server, use the amd64 package:

    sudo dpkg -i wkhtmltox_0.12.6.1-2.jammy_amd64.deb

If dependencies are missing:

    sudo apt --fix-broken install -y
    sudo dpkg --configure -a

Verify:

    wkhtmltopdf --version

Expected:

    wkhtmltopdf 0.12.6.1 (with patched qt)

---

## 8. Install Frappe Bench

Install Bench:

    sudo -H pip3 install frappe-bench --break-system-packages

Go to `/var/www`:

    cd /var/www

Initialize Frappe v16:

    bench init Frappe --frappe-branch version-16 --python python3.14

Enter the bench:

    cd /var/www/Frappe

Verify:

    bench version

> Do not manually create `/var/www/Frappe` before running `bench init`. Bench creates the directory.

---

## 9. Create Frappe Site

    cd /var/www/Frappe

    bench new-site pkdevops.online

    bench use pkdevops.online

    bench use

---

## 10. Install Helpdesk

    cd /var/www/Frappe

    bench get-app helpdesk --branch main

    bench install-app helpdesk

---

## 11. Install Telephony

    cd /var/www/Frappe

    bench get-app telephony --branch develop

    bench --site pkdevops.online install-app telephony

    bench --site pkdevops.online migrate

---

## 12. Configure Supervisor

Install Supervisor:

    sudo apt-get install -y supervisor

Generate configuration:

    cd /var/www/Frappe

    sudo bench setup supervisor

Create symlink:

    sudo ln -sf /var/www/Frappe/config/supervisor.conf /etc/supervisor/conf.d/Frappe.conf

Reload Supervisor:

    sudo supervisorctl reread
    sudo supervisorctl update

Check status:

    sudo supervisorctl status

All required Frappe processes should show `RUNNING`.

---

## 13. Configure Apache

Enable required modules:

    sudo a2enmod proxy proxy_http proxy_wstunnel rewrite headers alias

Create Apache configuration:

    sudo nano /etc/apache2/sites-available/pkdevops.online.conf

Add:

    <VirtualHost *:80>

        ServerName pkdevops.online

        Alias /assets /var/www/Frappe/sites/assets

        <Directory /var/www/Frappe/sites/assets>
            Require all granted
        </Directory>

        ProxyPass /assets !

        ProxyPreserveHost On
        ProxyRequests Off

        RewriteEngine On

        RewriteCond %{HTTP:Upgrade} =websocket [NC]
        RewriteRule /socket.io/(.*) ws://127.0.0.1:9000/socket.io/$1 [P,L]

        ProxyPass /socket.io http://127.0.0.1:9000/socket.io
        ProxyPassReverse /socket.io http://127.0.0.1:9000/socket.io

        ProxyPass / http://127.0.0.1:8000/
        ProxyPassReverse / http://127.0.0.1:8000/

        ErrorLog ${APACHE_LOG_DIR}/pkdevops.online-error.log
        CustomLog ${APACHE_LOG_DIR}/pkdevops.online-access.log combined

    </VirtualHost>

Enable the site:

    sudo a2ensite pkdevops.online.conf

Test Apache:

    sudo apachectl configtest

Expected:

    Syntax OK

Reload Apache:

    sudo systemctl reload apache2

Test assets:

    curl -Ik -H "Host: pkdevops.online" http://127.0.0.1/assets/frappe/images/frappe-favicon.svg

---

## 14. Configure SSL

Install Certbot:

    sudo apt-get install -y certbot python3-certbot-apache

Generate SSL:

    sudo certbot --apache -d pkdevops.online

Verify:

    sudo systemctl status apache2
    sudo supervisorctl status

Open:

    https://pkdevops.online

---

## 15. Location Customization Repository

Clone the customization repository:

    cd /var/www

    git clone https://github.com/KINGG777/Frappe-Location.git

Verify:

    ls -la /var/www

    tree /var/www/Frappe-Location

Expected structure:

    Frappe-Location/
    ├── README.md
    ├── desk/
    │   └── src/
    │       ├── components/
    │       │   ├── DynamicDoctypeForm.vue
    │       │   ├── contact/
    │       │   │   ├── EditContactDialog.vue
    │       │   │   └── NewContactDialog.vue
    │       │   ├── customer/
    │       │   │   └── InviteContactDialog.vue
    │       │   ├── layouts/
    │       │   │   └── layoutSettings.ts
    │       │   ├── location/
    │       │   │   └── NewLocationDialog.vue
    │       │   └── ticket/
    │       │       └── TicketCustomerSidebar.vue
    │       ├── composables/
    │       │   └── contact.ts
    │       ├── pages/
    │       │   └── location/
    │       │       ├── Location.vue
    │       │       └── Locations.vue
    │       ├── router/
    │       │   └── index.ts
    │       ├── types/
    │       │   └── doctypes.ts
    │       └── types.ts
    └── helpdesk/
        └── api/
            ├── contact.py
            └── doc.py

---

## 16. Backup Helpdesk

Before modifying Helpdesk source files:

    cd /var/www

    sudo cp -a Frappe/apps/helpdesk Frappe/apps/helpdesk.backup.$(date +%Y%m%d_%H%M%S)

    ls -ld /var/www/Frappe/apps/helpdesk.backup.*

---

## 17. Copy All Location Customization Files

All customization files:

    cd /var/www/Frappe-Location

    cp desk/src/components/DynamicDoctypeForm.vue /var/www/Frappe/apps/helpdesk/desk/src/components/

    cp -r desk/src/pages/location /var/www/Frappe/apps/helpdesk/desk/src/pages/

    cp -r desk/src/components/location /var/www/Frappe/apps/helpdesk/desk/src/components/

    cp desk/src/router/index.ts /var/www/Frappe/apps/helpdesk/desk/src/router/index.ts

    cp desk/src/components/layouts/layoutSettings.ts /var/www/Frappe/apps/helpdesk/desk/src/components/layouts/layoutSettings.ts

    cp desk/src/components/contact/NewContactDialog.vue /var/www/Frappe/apps/helpdesk/desk/src/components/contact/

    cp desk/src/components/contact/EditContactDialog.vue /var/www/Frappe/apps/helpdesk/desk/src/components/contact/

    cp desk/src/composables/contact.ts /var/www/Frappe/apps/helpdesk/desk/src/composables/

    cp desk/src/types.ts /var/www/Frappe/apps/helpdesk/desk/src/types.ts

    cp desk/src/types/doctypes.ts /var/www/Frappe/apps/helpdesk/desk/src/types/doctypes.ts

    cp helpdesk/api/contact.py /var/www/Frappe/apps/helpdesk/helpdesk/api/contact.py

    cp desk/src/components/ticket/TicketCustomerSidebar.vue /var/www/Frappe/apps/helpdesk/desk/src/components/ticket/

    cp helpdesk/api/doc.py /var/www/Frappe/apps/helpdesk/helpdesk/api/doc.py

    cp desk/src/components/customer/InviteContactDialog.vue /var/www/Frappe/apps/helpdesk/desk/src/components/customer/

---

## 18. Create Location DocType

Go to:

**Desk → DocType → New**

Create:

| Property | Value |
|---|---|
| Name | `Location` |
| Module | `Helpdesk` |

### Location Name

| Property | Value |
|---|---|
| Label | `Location Name` |
| Fieldname | `location_name` |
| Type | `Data` |
| Mandatory | Yes |
| Unique | Yes |

### Company

| Property | Value |
|---|---|
| Label | `Company` |
| Fieldname | `company` |
| Type | `Link` |
| Options | `HD Customer` |
| Mandatory | Yes |

Set Auto Name:

    field:location_name

---

## 19. ERPNext Location Conflict

If ERPNext is installed on the same site, `Location` may conflict with an ERPNext core DocType.

In that case use:

    HD Location

instead.

If `HD Location` is used, change all references from:

    "Location"

to:

    "HD Location"

Also change the Link field Options accordingly.

---

## 20. Configure Contact

Go to:

**Customize Form → Contact**

Add the Location field:

| Property | Value |
|---|---|
| Label | `Location` |
| Type | `Link` |
| Options | `Location` |
| Fieldname | `custom_location` |

The fieldname must remain:

    custom_location

---

## 21. Configure HD Ticket

Go to:

**Customize Form → HD Ticket**

Add:

| Property | Value |
|---|---|
| Label | `Location` |
| Type | `Link` |
| Options | `Location` |
| Fieldname | `custom_location` |
| Read Only | Yes |

The Location is automatically derived from the Contact.

---

## 22. Configure HD Ticket Template

Open the active:

**HD Ticket Template**

Inside the **Fields** child table, add:

    custom_location

Place it directly after:

    customer

---

## 23. Server Script - Auto Fill Ticket Location

Create a Server Script:

| Property | Value |
|---|---|
| Name | `Ticket-Field` |
| Script Type | `DocType Event` |
| Reference Document Type | `HD Ticket` |
| DocType Event | `Before Save` |

Use:

    if doc.contact:
        doc.custom_location = frappe.db.get_value(
            "Contact",
            doc.contact,
            "custom_location"
        )

Single-line alternative:

    doc.custom_location = frappe.db.get_value("Contact", doc.contact, "custom_location") if doc.contact else None

Flow:

    HD Ticket
        ↓
    Contact
        ↓
    Contact.custom_location
        ↓
    HD Ticket.custom_location

---

## 24. Server Script - Location Based Team Routing

Create another Server Script:

| Property | Value |
|---|---|
| Script Type | `DocType Event` |
| Reference Document Type | `HD Ticket` |
| DocType Event | `Before Save` |

Use:

    location = frappe.db.get_value("Contact", doc.contact, "custom_location") if doc.contact else None

    teams = frappe.get_all("HD Team", filters={"disabled": 0}, pluck="name")

    if location:
        matches = [t for t in teams if location.lower() in t.lower()]
        doc.agent_group = matches[0] if matches else doc.agent_group

### Routing Logic

The script:

1. Gets the Contact from the ticket.
2. Gets `custom_location` from the Contact.
3. Gets all enabled HD Teams.
4. Searches the team names for the Location.
5. Performs a case-insensitive match.
6. Assigns the first matching team to `agent_group`.

Example:

    Contact Location:
    Location A

Teams:

    Location A Team
    Location B Team
    Location C Team

Result:

    HD Ticket.agent_group = Location A Team

Recommended naming convention:

    Location A Team
    Location B Team
    Location C Team
    Location X Team
    Location Y Team
    Location Z Team

> If multiple teams match the same Location, the first matching team is selected.

---

## 25. Server Script - get_contact_customer API

Create a Server Script:

| Property | Value |
|---|---|
| Script Type | `API` |
| API Method | `get_contact_customer` |

Use:

    contact = frappe.form_dict.get("contact")

    if not contact:
        frappe.response["message"] = {
            "customer": None,
            "locations": []
        }
    else:
        members = frappe.get_all(
            "HD Customer Member",
            filters={"contact_name": contact},
            fields=["parent"],
            limit_page_length=1
        )

        customer = members[0].parent if members else None

        locations = []
        if customer:
            locations = frappe.get_all(
                "Location",
                filters={"company": customer},
                pluck="name"
            )

        frappe.response["message"] = {
            "customer": customer,
            "locations": locations
        }

---

## 26. Contact / Customer / Location Relationship

    Contact
       |
       v
    HD Customer Member
       |
       +-- contact_name = Contact
       |
       +-- parent = HD Customer
                 |
                 v
    Location
       |
       +-- company = HD Customer

Therefore:

    Contact
       ↓
    Customer
       ↓
    Customer Locations

---

## 27. Client Script - Contact Location Filter

Create a Client Script:

| Property | Value |
|---|---|
| DocType | `Contact` |
| Apply To | `Form` |

Use:

    frappe.ui.form.on("Contact", {
        refresh(frm) {
            set_location_filter(frm);
        },

        onload(frm) {
            set_location_filter(frm);
        }
    });

    async function set_location_filter(frm) {

        if (!frm.doc.name) {
            frm.set_query("custom_location", function () {
                return { filters: { name: "" } };
            });
            return;
        }

        try {
            const response = await frappe.call({
                method: "get_contact_customer",
                args: { contact: frm.doc.name }
            });

            const data = response.message || {};
            const locations = data.locations || [];

            frm.set_query("custom_location", function () {
                if (!locations.length) {
                    return { filters: { name: "" } };
                }

                return {
                    filters: {
                        name: ["in", locations]
                    }
                };
            });

        } catch (error) {
            console.error(error);

            frm.set_query("custom_location", function () {
                return { filters: { name: "" } };
            });
        }
    }

---

## 28. Location Filtering Flow

Example:

    Customer A
    ├── Location A
    ├── Location B
    └── Location C

A Contact belonging to Customer A will see:

    Location A
    Location B
    Location C

Locations belonging to another customer will not appear.

Flow:

    Open Contact
          ↓
    Get Contact Customer
          ↓
    get_contact_customer API
          ↓
    Get Customer Locations
          ↓
    Filter custom_location

---

## 29. Build Helpdesk

This is a direct server deployment.

There is no Docker frontend container.

The Helpdesk application is located at:

    /var/www/Frappe/apps/helpdesk

Build from the main bench:

    cd /var/www/Frappe

    bench build --app helpdesk

Do not run the build from:

    /var/www/Frappe-Location

The customization repository is only the source for the custom files.

---

## 30. Clear Cache and Migrate

    cd /var/www/Frappe

    bench --site pkdevops.online clear-cache

    bench --site pkdevops.online clear-website-cache

    bench --site pkdevops.online migrate

---

## 31. Restart Frappe

    cd /var/www/Frappe

    bench restart

Check Supervisor:

    sudo supervisorctl status

If necessary:

    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl restart all

---

## 32. Verify Apache

    sudo systemctl status apache2

    sudo apachectl configtest

    sudo systemctl reload apache2

Expected:

    Syntax OK

---

## 33. Verify MariaDB

    sudo systemctl status mariadb

---

## 34. Verify Redis

    sudo systemctl status redis-server

---

## 35. Verify Supervisor

    sudo supervisorctl status

All required Frappe processes should show:

    RUNNING

---

## 36. Verify Installed Applications

    cd /var/www/Frappe

    bench --site pkdevops.online list-apps

Expected:

    frappe
    helpdesk
    telephony

---

## 37. Verify Site

    ls -la /var/www/Frappe/sites/

Expected:

    pkdevops.online
    assets
    common_site_config.json

Check site:

    cd /var/www/Frappe

    bench --site pkdevops.online doctor

---

## 38. Verify Helpdesk Files

    ls -la /var/www/Frappe/apps/helpdesk

    ls -la /var/www/Frappe/apps/helpdesk/desk/src/components/customer/

    ls -la /var/www/Frappe/apps/helpdesk/desk/src/components/contact/

    ls -la /var/www/Frappe/apps/helpdesk/desk/src/components/location/

    ls -la /var/www/Frappe/apps/helpdesk/desk/src/components/ticket/

    ls -la /var/www/Frappe/apps/helpdesk/desk/src/pages/location/

---

## 39. Verify Location Assets

    find /var/www/Frappe/apps/helpdesk -type f \
    \( -name "Location-*.js" -o -name "Locations-*.js" \)

---

## 40. Browser Cache

After frontend changes, perform a hard refresh:

    CTRL + SHIFT + R

If required:

    Chrome DevTools
    → Network
    → Disable cache
    → Reload

---

# Troubleshooting

## Bench Already Exists

If you see:

    ERROR: Bench instance already exists

and `/var/www/Frappe` is only an empty manually-created directory:

    cd /var/www

    rmdir Frappe

Then:

    bench init Frappe --frappe-branch version-16 --python python3.14

> Never remove an existing production bench containing application or site data.

---

## Node.js Version Error

Check:

    node -v

Install/use Node.js 24:

    nvm install 24
    nvm use 24
    node -v

---

## wkhtmltopdf Dependency Error

    sudo apt-get install xvfb libfontconfig fontconfig -y

    sudo apt-get install xfonts-75dpi -y

    sudo apt --fix-broken install -y

    sudo dpkg --configure -a

Verify:

    wkhtmltopdf --version

---

## Supervisor Processes Not Running

    sudo supervisorctl status

    sudo supervisorctl reread

    sudo supervisorctl update

    sudo supervisorctl restart all

---

## Apache Configuration Error

Test:

    sudo apachectl configtest

Check error log:

    sudo tail -f /var/log/apache2/pkdevops.online-error.log

Check access log:

    sudo tail -f /var/log/apache2/pkdevops.online-access.log

---

## Frappe Logs

    cd /var/www/Frappe

    ls -la logs

    tail -f /var/www/Frappe/logs/*.log

---

## Location Not Showing

Check custom files:

    ls -la /var/www/Frappe/apps/helpdesk/desk/src/components/location/

    ls -la /var/www/Frappe/apps/helpdesk/desk/src/pages/location/

Rebuild:

    cd /var/www/Frappe

    bench build --app helpdesk

Clear cache:

    bench --site pkdevops.online clear-cache

    bench --site pkdevops.online clear-website-cache

Restart:

    bench restart

Hard refresh:

    CTRL + SHIFT + R

---

## Ticket Location Not Populating

Verify:

1. Contact has `custom_location`.
2. HD Ticket has `custom_location`.
3. Ticket Location field is Read Only.
4. `Ticket-Field` Server Script is enabled.
5. Server Script is configured for `HD Ticket`.
6. Event is `Before Save`.

Clear cache:

    cd /var/www/Frappe

    bench --site pkdevops.online clear-cache

    bench restart

---

## Team Routing Not Working

Verify:

1. Contact has a Location.
2. Location exists.
3. HD Team is enabled.
4. Team name contains the Location name.
5. Location-based Team Routing Server Script is enabled.
6. Script is configured for `HD Ticket`.
7. Event is `Before Save`.

Check teams:

    cd /var/www/Frappe

    bench --site pkdevops.online console

Then:

    frappe.get_all("HD Team", filters={"disabled": 0}, pluck="name")

---

# 41. Important Paths

| Component | Path |
|---|---|
| Main Bench | `/var/www/Frappe` |
| Frappe Core | `/var/www/Frappe/apps/frappe` |
| Helpdesk | `/var/www/Frappe/apps/helpdesk` |
| Helpdesk Frontend | `/var/www/Frappe/apps/helpdesk/desk` |
| Helpdesk Backend | `/var/www/Frappe/apps/helpdesk/helpdesk` |
| Customer Components | `/var/www/Frappe/apps/helpdesk/desk/src/components/customer` |
| Contact Components | `/var/www/Frappe/apps/helpdesk/desk/src/components/contact` |
| Location Components | `/var/www/Frappe/apps/helpdesk/desk/src/components/location` |
| Location Pages | `/var/www/Frappe/apps/helpdesk/desk/src/pages/location` |
| Site | `/var/www/Frappe/sites/pkdevops.online` |
| Assets | `/var/www/Frappe/sites/assets` |
| Customization Source | `/var/www/Frappe-Location` |
| Supervisor Config | `/var/www/Frappe/config/supervisor.conf` |
| Apache Config | `/etc/apache2/sites-available/pkdevops.online.conf` |

---

# 42. Future Customization Updates

When files in `/var/www/Frappe-Location` are changed, create a new Helpdesk backup:

    cd /var/www

    sudo cp -a Frappe/apps/helpdesk Frappe/apps/helpdesk.backup.$(date +%Y%m%d_%H%M%S)

Copy all customization files:

    cd /var/www/Frappe-Location

    cp desk/src/components/DynamicDoctypeForm.vue /var/www/Frappe/apps/helpdesk/desk/src/components/

    cp -r desk/src/pages/location /var/www/Frappe/apps/helpdesk/desk/src/pages/

    cp -r desk/src/components/location /var/www/Frappe/apps/helpdesk/desk/src/components/

    cp desk/src/router/index.ts /var/www/Frappe/apps/helpdesk/desk/src/router/index.ts

    cp desk/src/components/layouts/layoutSettings.ts /var/www/Frappe/apps/helpdesk/desk/src/components/layouts/layoutSettings.ts

    cp desk/src/components/contact/NewContactDialog.vue /var/www/Frappe/apps/helpdesk/desk/src/components/contact/

    cp desk/src/components/contact/EditContactDialog.vue /var/www/Frappe/apps/helpdesk/desk/src/components/contact/

    cp desk/src/composables/contact.ts /var/www/Frappe/apps/helpdesk/desk/src/composables/

    cp desk/src/types.ts /var/www/Frappe/apps/helpdesk/desk/src/types.ts

    cp desk/src/types/doctypes.ts /var/www/Frappe/apps/helpdesk/desk/src/types/doctypes.ts

    cp helpdesk/api/contact.py /var/www/Frappe/apps/helpdesk/helpdesk/api/contact.py

    cp desk/src/components/ticket/TicketCustomerSidebar.vue /var/www/Frappe/apps/helpdesk/desk/src/components/ticket/

    cp helpdesk/api/doc.py /var/www/Frappe/apps/helpdesk/helpdesk/api/doc.py

    cd /var/www/Frappe/apps/helpdesk/desk/src/components/customer

    cp InviteContactDialog.vue InviteContactDialog.vue.bk

    sudo vi InviteContactDialog.vue

Build and restart:

    cd /var/www/Frappe

    bench build --app helpdesk

    bench --site pkdevops.online clear-cache

    bench --site pkdevops.online clear-website-cache

    bench --site pkdevops.online migrate

    bench restart

    sudo supervisorctl status

---

# 43. Backup

## Backup Helpdesk Application

    cd /var/www

    sudo cp -a Frappe/apps/helpdesk Frappe/apps/helpdesk.backup.$(date +%Y%m%d_%H%M%S)

List backups:

    ls -ld /var/www/Frappe/apps/helpdesk.backup.*

---

# 44. Production Update Quick Commands

For normal Helpdesk customization updates:

    cd /var/www/Frappe

    bench build --app helpdesk

    bench --site pkdevops.online clear-cache

    bench --site pkdevops.online clear-website-cache

    bench --site pkdevops.online migrate

    bench restart

    sudo supervisorctl status

Then hard refresh:

    CTRL + SHIFT + R

---

# 45. Direct Installation - No Docker

This deployment is a direct Ubuntu installation.

Do NOT use:

    docker ps
    docker exec
    docker cp
    docker compose

There is no Docker backend container.

There is no Docker frontend container.

Actual Helpdesk source:

    /var/www/Frappe/apps/helpdesk

Customization source:

    /var/www/Frappe-Location

Correct build command:

    cd /var/www/Frappe

    bench build --app helpdesk

---

# 46. Final Verification Checklist

## Server

- [ ] Ubuntu updated
- [ ] Apache installed
- [ ] Apache running
- [ ] Python 3.14 installed
- [ ] Node.js 24 installed
- [ ] Yarn installed
- [ ] MariaDB installed
- [ ] MariaDB running
- [ ] Redis installed
- [ ] Redis running
- [ ] wkhtmltopdf installed

## Frappe

- [ ] Frappe Bench initialized
- [ ] Site `pkdevops.online` created
- [ ] Helpdesk installed
- [ ] Telephony installed
- [ ] Supervisor configured
- [ ] Supervisor processes running
- [ ] Apache reverse proxy configured
- [ ] SSL configured

## Location Customization

- [ ] `Frappe-Location` repository cloned
- [ ] Helpdesk backup created
- [ ] `DynamicDoctypeForm.vue` copied
- [ ] Location pages copied
- [ ] Location components copied
- [ ] Router copied
- [ ] Layout settings copied
- [ ] Contact dialogs copied
- [ ] Contact composable copied
- [ ] Types copied
- [ ] Contact API copied
- [ ] Ticket Customer Sidebar copied
- [ ] Document API copied
- [ ] `InviteContactDialog.vue` customized
- [ ] `InviteContactDialog.vue.bk` created
- [ ] Helpdesk frontend built

## Frappe Configuration

- [ ] Location DocType created
- [ ] Contact `custom_location` created
- [ ] HD Ticket `custom_location` created
- [ ] HD Ticket Template updated
- [ ] Ticket Location Server Script created
- [ ] Location Team Routing Server Script created
- [ ] `get_contact_customer` API created
- [ ] Contact Client Script created

## Testing

- [ ] Contact Location filtering works
- [ ] Contact Location saves correctly
- [ ] New ticket gets Location automatically
- [ ] Ticket Location is read-only
- [ ] Location-based team routing works
- [ ] Helpdesk Location page opens
- [ ] Location list works
- [ ] Location creation works
- [ ] Invite Contact customization works
- [ ] Website loads through HTTPS
- [ ] No frontend JavaScript 404 errors
- [ ] No relevant errors in browser console
- [ ] No relevant errors in Frappe logs

---

# Final System Flow

    HD CUSTOMER
         |
         +------------------+------------------+
         |                  |                  |
         v                  v                  v
    Location A         Location B         Location C
         |
         v
      Contact
         |
         | custom_location
         v
     HD Ticket
         |
         v
 Location Team Matching
         |
         v
      HD Team
         |
         v
    agent_group

---

# Production Commands Summary

## Start / Restart

    cd /var/www/Frappe

    bench restart

## Build

    cd /var/www/Frappe

    bench build --app helpdesk

## Clear Cache

    cd /var/www/Frappe

    bench --site pkdevops.online clear-cache

    bench --site pkdevops.online clear-website-cache

## Migrate

    cd /var/www/Frappe

    bench --site pkdevops.online migrate

## Supervisor

    sudo supervisorctl status

## Apache

    sudo systemctl status apache2

    sudo apachectl configtest

## MariaDB

    sudo systemctl status mariadb

## Redis

    sudo systemctl status redis-server

---

# End

**Frappe Bench:** `/var/www/Frappe`

**Helpdesk:** `/var/www/Frappe/apps/helpdesk`

**Location Customization:** `/var/www/Frappe-Location`

**Production Domain:** `https://pkdevops.online`
