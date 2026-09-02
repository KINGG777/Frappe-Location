# Frappe Helpdesk v16 — Direct Server Deployment & Location Customization

Production deployment guide for **Frappe Helpdesk v16** on Ubuntu using a direct server installation.

> **Deployment type:** Direct Ubuntu installation
> **Bench:** `/var/www/Frappe`
> **Customization source:** `/var/www/Frappe-Location`
> **Site:** `pkdevops.online`
> **Web server:** Apache
> **Process manager:** Supervisor
> **Database:** MariaDB
> **Cache/Queue:** Redis
> **Node.js:** 24
> **Python:** 3.14

---

## Table of Contents

1. [Architecture](#architecture)
2. [Prerequisites](#prerequisites)
3. [System Update](#1-system-update)
4. [Install Apache](#2-install-apache)
5. [Install Python 314](#3-install-python-314)
6. [Install MariaDB](#4-install-mariadb)
7. [Install Redis](#5-install-redis)
8. [Install Node.js and Yarn](#6-install-nodejs-and-yarn)
9. [Install wkhtmltopdf](#7-install-wkhtmltopdf)
10. [Install Frappe Bench](#8-install-frappe-bench)
11. [Create Site](#9-create-frappe-site)
12. [Install Helpdesk](#10-install-helpdesk)
13. [Install Telephony](#11-install-telephony)
14. [Configure Supervisor](#12-configure-supervisor)
15. [Configure Apache](#13-configure-apache)
16. [Configure SSL](#14-configure-ssl)
17. [Location Customization](#15-location-customization)
18. [Create Location DocType](#16-create-location-doctype)
19. [Contact Configuration](#17-configure-contact)
20. [Ticket Configuration](#18-configure-hd-ticket)
21. [Server Scripts](#19-server-scripts)
22. [Client Script](#20-client-script)
23. [Build Customization](#21-build-helpdesk)
24. [Restart and Clear Cache](#22-restart-and-clear-cache)
25. [Verification](#23-verification)
26. [Troubleshooting](#24-troubleshooting)
27. [Future Updates](#25-future-updates)
28. [Backup](#26-backup)

---

# Architecture

```text
                         Internet
                            |
                            v
                    +---------------+
                    |    Apache     |
                    |    :80/:443   |
                    +-------+-------+
                            |
                            v
                    +---------------+
                    | Frappe Bench  |
                    |    :8000      |
                    +-------+-------+
                            |
             +--------------+--------------+
             |                             |
             v                             v
       +-----------+                +-----------+
       | Helpdesk  |                |  Frappe   |
       |   App     |                |   Core    |
       +-----+-----+                +-----------+
             |
             v
      +----------------+
      | Location       |
      | Customization  |
      +-------+--------+
              |
              v
        +-----------+
        |  Contact  |
        +-----+-----+
              |
              | custom_location
              v
        +-----------+
        | Location  |
        +-----+-----+
              |
              v
        +-----------+
        | HD Ticket |
        +-----+-----+
              |
              v
        +-----------+
        | HD Team   |
        +-----------+
```

### Ticket flow

```text
Contact
   |
   v
Contact.custom_location
   |
   v
HD Ticket.custom_location
   |
   v
Location-based team matching
   |
   v
HD Ticket.agent_group
```

---

# Prerequisites

Before starting, make sure you have:

* Ubuntu server
* Root or sudo access
* Domain pointing to the server
* `pkdevops.online` pointing to the server
* Required ports open:

  * `80`
  * `443`
  * `22`
* Sufficient server resources for Frappe/Helpdesk
* MariaDB
* Redis
* Python 3.14
* Node.js 24

---

# 1. System Update

```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
```

---

# 2. Install Apache

```bash
sudo apt install apache2 -y
```

Enable Apache:

```bash
sudo systemctl enable apache2
sudo systemctl start apache2
```

Verify:

```bash
sudo systemctl status apache2
```

---

# 3. Install Python 3.14

```bash
sudo apt install python3.14 python3.14-venv -y
```

Install pip:

```bash
python3.14 -m ensurepip --upgrade
```

Add local binaries to PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Verify:

```bash
pip3.14 --version
```

Upgrade pip:

```bash
python3.14 -m pip install --upgrade pip
```

Install required packages:

```bash
sudo apt-get install python3-setuptools python3-pip -y
sudo apt install pkg-config -y
sudo apt install python3.14-dev -y
```

---

# 4. Install MariaDB

```bash
sudo apt install mariadb-server -y
```

Run the secure installation:

```bash
sudo mysql_secure_installation
```

Install MariaDB development libraries:

```bash
sudo apt-get install libmysqlclient-dev -y
```

Enable and start MariaDB:

```bash
sudo systemctl enable mariadb
sudo systemctl start mariadb
```

Verify:

```bash
sudo systemctl status mariadb
```

---

# 5. Install Redis

```bash
sudo apt-get install redis-server -y
```

Enable and start Redis:

```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

Verify:

```bash
sudo systemctl status redis-server
```

---

# 6. Install Node.js and Yarn

Install curl:

```bash
sudo apt install curl -y
```

Install NVM:

```bash
curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
```

Reload the shell:

```bash
source ~/.profile
```

Install npm:

```bash
sudo apt-get install npm -y
```

Install Yarn:

```bash
sudo npm install -g yarn
```

Install Node.js 24:

```bash
nvm install 24
nvm use 24
```

Verify:

```bash
node -v
npm -v
yarn -v
```

Expected Node.js version:

```text
v24.x.x
```

---

# 7. Install wkhtmltopdf

Install required dependencies:

```bash
sudo apt-get install xvfb libfontconfig fontconfig -y
sudo apt-get install xfonts-75dpi -y
```

Check server architecture:

```bash
uname -m
```

For an x86_64 server, install the amd64 package:

```bash
sudo dpkg -i wkhtmltox_0.12.6.1-2.jammy_amd64.deb
```

If dependency errors occur:

```bash
sudo apt --fix-broken install -y
```

Then:

```bash
sudo dpkg --configure -a
```

Verify:

```bash
wkhtmltopdf --version
```

Expected:

```text
wkhtmltopdf 0.12.6.1 (with patched qt)
```

---

# 8. Install Frappe Bench

Install Bench:

```bash
sudo -H pip3 install frappe-bench --break-system-packages
```

Go to `/var/www`:

```bash
cd /var/www
```

> Do not manually create `/var/www/Frappe` before running `bench init`.

Initialize Frappe v16:

```bash
bench init Frappe --frappe-branch version-16 --python python3.14
```

Enter the bench:

```bash
cd /var/www/Frappe
```

Verify:

```bash
bench version
```

---

# 9. Create Frappe Site

```bash
cd /var/www/Frappe

bench new-site pkdevops.online
```

Set the site as default:

```bash
bench use pkdevops.online
```

Verify:

```bash
bench use
```

---

# 10. Install Helpdesk

Get Helpdesk:

```bash
cd /var/www/Frappe

bench get-app helpdesk --branch main
```

Install Helpdesk:

```bash
bench install-app helpdesk
```

---

# 11. Install Telephony

Get Telephony:

```bash
cd /var/www/Frappe

bench get-app telephony --branch develop
```

Install Telephony:

```bash
bench --site pkdevops.online install-app telephony
```

Run migration:

```bash
bench --site pkdevops.online migrate
```

---

# 12. Configure Supervisor

Install Supervisor:

```bash
sudo apt-get install -y supervisor
```

Generate Supervisor configuration:

```bash
cd /var/www/Frappe

sudo bench setup supervisor
```

Create the Supervisor symlink:

```bash
sudo ln -sf /var/www/Frappe/config/supervisor.conf /etc/supervisor/conf.d/Frappe.conf
```

Reload Supervisor:

```bash
sudo supervisorctl reread
sudo supervisorctl update
```

Check:

```bash
sudo supervisorctl status
```

---

# 13. Configure Apache

Enable required modules:

```bash
sudo a2enmod proxy proxy_http proxy_wstunnel rewrite headers alias
```

Create the virtual host:

```bash
sudo nano /etc/apache2/sites-available/pkdevops.online.conf
```

Use:

```apache
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
```

Enable the site:

```bash
sudo a2ensite pkdevops.online.conf
```

Test Apache configuration:

```bash
sudo apachectl configtest
```

Expected:

```text
Syntax OK
```

Reload Apache:

```bash
sudo systemctl reload apache2
```

Test assets:

```bash
curl -Ik -H "Host: pkdevops.online" http://127.0.0.1/assets/frappe/images/frappe-favicon.svg
```

---

# 14. Configure SSL

Install Certbot:

```bash
sudo apt-get install -y certbot python3-certbot-apache
```

Generate SSL certificate:

```bash
sudo certbot --apache -d pkdevops.online
```

Verify:

```bash
sudo systemctl status apache2
```

Open:

```text
https://pkdevops.online
```

---

# 15. Location Customization

The custom Location source is stored at:

```text
/var/www/Frappe-Location
```

Expected structure:

```text
/var/www/Frappe-Location/
├── README.md
├── desk/
│   └── src/
│       ├── components/
│       │   ├── DynamicDoctypeForm.vue
│       │   ├── contact/
│       │   │   ├── EditContactDialog.vue
│       │   │   └── NewContactDialog.vue
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
```

---

# 16. Create Backup Before Customization

Before modifying the Helpdesk application:

```bash
cd /var/www

sudo cp -a Frappe/apps/helpdesk \
Frappe/apps/helpdesk.backup.$(date +%Y%m%d_%H%M%S)
```

Verify:

```bash
ls -ld /var/www/Frappe/apps/helpdesk.backup.*
```

---

# 17. Copy Location Customization Files

Go to the customization repository:

```bash
cd /var/www/Frappe-Location
```

Copy `DynamicDoctypeForm.vue`:

```bash
cp desk/src/components/DynamicDoctypeForm.vue \
/var/www/Frappe/apps/helpdesk/desk/src/components/
```

Copy Location pages:

```bash
cp -r desk/src/pages/location \
/var/www/Frappe/apps/helpdesk/desk/src/pages/
```

Copy Location components:

```bash
cp -r desk/src/components/location \
/var/www/Frappe/apps/helpdesk/desk/src/components/
```

Copy router:

```bash
cp desk/src/router/index.ts \
/var/www/Frappe/apps/helpdesk/desk/src/router/index.ts
```

Copy layout settings:

```bash
cp desk/src/components/layouts/layoutSettings.ts \
/var/www/Frappe/apps/helpdesk/desk/src/components/layouts/layoutSettings.ts
```

Copy New Contact dialog:

```bash
cp desk/src/components/contact/NewContactDialog.vue \
/var/www/Frappe/apps/helpdesk/desk/src/components/contact/
```

Copy Edit Contact dialog:

```bash
cp desk/src/components/contact/EditContactDialog.vue \
/var/www/Frappe/apps/helpdesk/desk/src/components/contact/
```

Copy Contact composable:

```bash
cp desk/src/composables/contact.ts \
/var/www/Frappe/apps/helpdesk/desk/src/composables/
```

Copy types:

```bash
cp desk/src/types.ts \
/var/www/Frappe/apps/helpdesk/desk/src/types.ts
```

Copy DocType types:

```bash
cp desk/src/types/doctypes.ts \
/var/www/Frappe/apps/helpdesk/desk/src/types/doctypes.ts
```

Copy Contact API:

```bash
cp helpdesk/api/contact.py \
/var/www/Frappe/apps/helpdesk/helpdesk/api/contact.py
```

Copy Ticket Customer Sidebar:

```bash
cp desk/src/components/ticket/TicketCustomerSidebar.vue \
/var/www/Frappe/apps/helpdesk/desk/src/components/ticket/
```

Copy Doc API:

```bash
cp helpdesk/api/doc.py \
/var/www/Frappe/apps/helpdesk/helpdesk/api/doc.py
```

---

# 18. Create Location DocType

Navigate in Frappe:

**Desk → DocType → New**

Create:

| Setting | Value      |
| ------- | ---------- |
| Name    | `Location` |
| Module  | `Helpdesk` |

### Field: Location Name

| Property  | Value           |
| --------- | --------------- |
| Label     | `Location Name` |
| Fieldname | `location_name` |
| Type      | `Data`          |
| Mandatory | Yes             |
| Unique    | Yes             |

### Field: Company

| Property  | Value         |
| --------- | ------------- |
| Label     | `Company`     |
| Fieldname | `company`     |
| Type      | `Link`        |
| Options   | `HD Customer` |
| Mandatory | Yes           |

### Auto Name

Set:

```text
field:location_name
```

---

# 19. ERPNext Location Conflict

If ERPNext is installed on the same site, the name `Location` may conflict with an ERPNext core DocType.

In that case, use:

```text
HD Location
```

instead.

If using `HD Location`, update all code references from:

```python
"Location"
```

to:

```python
"HD Location"
```

Also update the Link field Options.

---

# 20. Configure Contact

Go to:

**Customize Form → Contact**

Add:

| Property  | Value             |
| --------- | ----------------- |
| Label     | `Location`        |
| Type      | `Link`            |
| Options   | `Location`        |
| Fieldname | `custom_location` |

The fieldname must be:

```text
custom_location
```

---

# 21. Configure HD Ticket

Go to:

**Customize Form → HD Ticket**

Add:

| Property  | Value             |
| --------- | ----------------- |
| Label     | `Location`        |
| Type      | `Link`            |
| Options   | `Location`        |
| Fieldname | `custom_location` |
| Read Only | Yes               |

---

# 22. Configure HD Ticket Template

Open the active **HD Ticket Template**.

Inside the **Fields** child table, add:

```text
custom_location
```

Place it directly after:

```text
customer
```

---

# 23. Server Script – Auto Fill Ticket Location

Create a Server Script.

| Property                | Value           |
| ----------------------- | --------------- |
| Name                    | `Ticket-Field`  |
| Script Type             | `DocType Event` |
| Reference Document Type | `HD Ticket`     |
| DocType Event           | `Before Save`   |

Use:

```python
if doc.contact:
    doc.custom_location = frappe.db.get_value(
        "Contact",
        doc.contact,
        "custom_location"
    )
```

If the Server Script editor causes formatting issues, use the single-line version:

```python
doc.custom_location = frappe.db.get_value("Contact", doc.contact, "custom_location") if doc.contact else None
```

### Flow

```text
HD Ticket
    ↓
Contact
    ↓
Contact.custom_location
    ↓
HD Ticket.custom_location
```

---

# 24. Server Script – Location Based Team Routing

Create another Server Script.

| Property                | Value           |
| ----------------------- | --------------- |
| Script Type             | `DocType Event` |
| Reference Document Type | `HD Ticket`     |
| DocType Event           | `Before Save`   |

Use:

```python
location = frappe.db.get_value("Contact", doc.contact, "custom_location") if doc.contact else None

teams = frappe.get_all("HD Team", filters={"disabled": 0}, pluck="name")

if location:
    matches = [t for t in teams if location.lower() in t.lower()]
    doc.agent_group = matches[0] if matches else doc.agent_group
```

### How it works

1. Gets the Contact from the ticket.
2. Gets the Contact's `custom_location`.
3. Gets all enabled `HD Team` records.
4. Searches team names for the Location.
5. Performs case-insensitive matching.
6. Assigns the first matching team to `agent_group`.

Example:

```text
Location:
Location A
```

Available teams:

```text
Location A Team
Location B Team
Location C Team
```

Result:

```text
HD Ticket.agent_group = Location A Team
```

### Recommended Team Naming

Use a consistent naming convention:

```text
Location A Team
Location B Team
Location C Team
Location X Team
Location Y Team
Location Z Team
```

> If multiple teams match the same Location, the first matching team is selected.

---

# 25. Server Script – get_contact_customer API

Create a Server Script:

| Property    | Value                  |
| ----------- | ---------------------- |
| Script Type | `API`                  |
| API Method  | `get_contact_customer` |

Use:

```python
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
```

---

# 26. Contact / Customer / Location Relationship

The data relationship is:

```text
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
```

Therefore:

```text
Contact
   ↓
Customer
   ↓
Customer Locations
```

---

# 27. Client Script – Filter Contact Locations

Create a Client Script.

| Property | Value     |
| -------- | --------- |
| DocType  | `Contact` |
| Apply To | `Form`    |

Use:

```javascript
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
```

---

# 28. Location Filtering Flow

Example customer:

```text
Customer A
├── Location A
├── Location B
└── Location C
```

A Contact belonging to Customer A will see:

```text
Location A
Location B
Location C
```

Locations belonging to another customer will not appear.

Flow:

```text
Open Contact
      ↓
Get Contact Customer
      ↓
get_contact_customer API
      ↓
Get Customer Locations
      ↓
Filter custom_location
```

---

# 29. Build Helpdesk Frontend

After copying all customization files, the build must be executed from the **main Frappe bench**.

Correct:

```bash
cd /var/www/Frappe
bench build --app helpdesk
```

Do not run the build from:

```text
/var/www/Frappe-Location
```

The customization repository is only the source of the custom files.

The actual Helpdesk application is:

```text
/var/www/Frappe/apps/helpdesk
```

The build may generate assets such as:

```text
Location-*.js
Locations-*.js
DynamicDoctypeForm.vue_*.js
```

Build warnings related to Browserslist, chunk sizes, CSS size, or Vue naming do not necessarily mean the build failed.

The important result is a successful build such as:

```text
✓ built
Done
```

---

# 30. Clear Cache and Migrate

```bash
cd /var/www/Frappe

bench --site pkdevops.online clear-cache

bench --site pkdevops.online clear-website-cache

bench --site pkdevops.online migrate
```

---

# 31. Restart Frappe

```bash
cd /var/www/Frappe

bench restart
```

Check Supervisor:

```bash
sudo supervisorctl status
```

If required:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart all
```

---

# 32. Verify Apache

Check Apache:

```bash
sudo systemctl status apache2
```

Test configuration:

```bash
sudo apachectl configtest
```

Expected:

```text
Syntax OK
```

Reload:

```bash
sudo systemctl reload apache2
```

---

# 33. Verify MariaDB

```bash
sudo systemctl status mariadb
```

---

# 34. Verify Redis

```bash
sudo systemctl status redis-server
```

---

# 35. Verify Supervisor

```bash
sudo supervisorctl status
```

All required Frappe processes should be running.

---

# 36. Verify Installed Applications

```bash
cd /var/www/Frappe

bench --site pkdevops.online list-apps
```

Expected applications:

```text
frappe
helpdesk
telephony
```

---

# 37. Verify Site

List sites:

```bash
ls -la /var/www/Frappe/sites/
```

Expected:

```text
pkdevops.online
assets
common_site_config.json
```

Check site health:

```bash
cd /var/www/Frappe

bench --site pkdevops.online doctor
```

---

# 38. Verify Helpdesk Build

Find generated Location assets:

```bash
find /var/www/Frappe/apps/helpdesk -type f \
\( -name "Location-*.js" -o -name "Locations-*.js" \)
```

Check Helpdesk public files:

```bash
find /var/www/Frappe/apps/helpdesk/helpdesk/public/desk \
-maxdepth 1 -type f | head
```

---

# 39. Browser Cache

After frontend changes, perform a hard refresh:

```text
CTRL + SHIFT + R
```

If required, open Chrome DevTools:

```text
DevTools
→ Network
→ Disable cache
→ Reload
```

---

# Troubleshooting

## Bench Already Exists

If you see:

```text
ERROR: Bench instance already exists
```

and `/var/www/Frappe` is an empty manually-created directory:

```bash
cd /var/www
rmdir Frappe
```

Then:

```bash
bench init Frappe --frappe-branch version-16 --python python3.14
```

> Never remove an existing production bench containing application/site data.

---

## `bench build` Says "No Such Command"

Make sure you are inside the actual Frappe bench:

```bash
cd /var/www/Frappe
```

Then:

```bash
bench build --app helpdesk
```

Do not run:

```bash
cd /var/www/Frappe-Location
bench build
```

---

## Node.js Version Problem

Check:

```bash
node -v
```

Use Node.js 24:

```bash
nvm install 24
nvm use 24
```

Verify:

```bash
node -v
```

---

## wkhtmltopdf Dependency Problem

Run:

```bash
sudo apt-get install xvfb libfontconfig fontconfig -y
sudo apt-get install xfonts-75dpi -y
sudo apt --fix-broken install -y
sudo dpkg --configure -a
```

Verify:

```bash
wkhtmltopdf --version
```

---

## Supervisor Processes Not Running

Check:

```bash
sudo supervisorctl status
```

Reload:

```bash
sudo supervisorctl reread
sudo supervisorctl update
```

Restart:

```bash
sudo supervisorctl restart all
```

---

## Apache Configuration Error

Run:

```bash
sudo apachectl configtest
```

Expected:

```text
Syntax OK
```

Check error log:

```bash
sudo tail -f /var/log/apache2/pkdevops.online-error.log
```

Check access log:

```bash
sudo tail -f /var/log/apache2/pkdevops.online-access.log
```

---

## Frappe Logs

```bash
cd /var/www/Frappe

ls -la logs
```

View logs:

```bash
tail -f /var/www/Frappe/logs/*.log
```

---

# Important Paths

| Component            | Path                                                |
| -------------------- | --------------------------------------------------- |
| Main Bench           | `/var/www/Frappe`                                   |
| Frappe               | `/var/www/Frappe/apps/frappe`                       |
| Helpdesk             | `/var/www/Frappe/apps/helpdesk`                     |
| Helpdesk Frontend    | `/var/www/Frappe/apps/helpdesk/desk`                |
| Helpdesk Backend     | `/var/www/Frappe/apps/helpdesk/helpdesk`            |
| Site                 | `/var/www/Frappe/sites/pkdevops.online`             |
| Shared Assets        | `/var/www/Frappe/sites/assets`                      |
| Customization Source | `/var/www/Frappe-Location`                          |
| Supervisor Config    | `/var/www/Frappe/config/supervisor.conf`            |
| Apache Config        | `/etc/apache2/sites-available/pkdevops.online.conf` |

---

# Direct Installation vs Docker

This installation is a **direct Ubuntu installation**.

Do not use Docker commands:

```bash
docker ps
docker exec
docker cp
docker compose
```

There is no frontend container.

The Helpdesk application is directly located at:

```text
/var/www/Frappe/apps/helpdesk
```

The correct frontend build command is:

```bash
cd /var/www/Frappe
bench build --app helpdesk
```

---

# Backup

## Backup Helpdesk Application

```bash
cd /var/www

sudo cp -a Frappe/apps/helpdesk \
Frappe/apps/helpdesk.backup.$(date +%Y%m%d_%H%M%S)
```

List backups:

```bash
ls -ld /var/www/Frappe/apps/helpdesk.backup.*
```

---

# Future Customization Update

When files in `/var/www/Frappe-Location` are changed, copy them again:

```bash
cd /var/www/Frappe-Location

cp desk/src/components/DynamicDoctypeForm.vue \
/var/www/Frappe/apps/helpdesk/desk/src/components/

cp -r desk/src/pages/location \
/var/www/Frappe/apps/helpdesk/desk/src/pages/

cp -r desk/src/components/location \
/var/www/Frappe/apps/helpdesk/desk/src/components/

cp desk/src/router/index.ts \
/var/www/Frappe/apps/helpdesk/desk/src/router/index.ts

cp desk/src/components/layouts/layoutSettings.ts \
/var/www/Frappe/apps/helpdesk/desk/src/components/layouts/layoutSettings.ts

cp desk/src/components/contact/NewContactDialog.vue \
/var/www/Frappe/apps/helpdesk/desk/src/components/contact/

cp desk/src/components/contact/EditContactDialog.vue \
/var/www/Frappe/apps/helpdesk/desk/src/components/contact/

cp desk/src/composables/contact.ts \
/var/www/Frappe/apps/helpdesk/desk/src/composables/

cp desk/src/types.ts \
/var/www/Frappe/apps/helpdesk/desk/src/types.ts

cp desk/src/types/doctypes.ts \
/var/www/Frappe/apps/helpdesk/desk/src/types/doctypes.ts

cp helpdesk/api/contact.py \
/var/www/Frappe/apps/helpdesk/helpdesk/api/contact.py

cp desk/src/components/ticket/TicketCustomerSidebar.vue \
/var/www/Frappe/apps/helpdesk/desk/src/components/ticket/

cp helpdesk/api/doc.py \
/var/www/Frappe/apps/helpdesk/helpdesk/api/doc.py
```

Then rebuild:

```bash
cd /var/www/Frappe

bench build --app helpdesk

bench --site pkdevops.online clear-cache

bench --site pkdevops.online clear-website-cache

bench --site pkdevops.online migrate

bench restart

sudo supervisorctl status
```

Finally perform a hard refresh:

```text
CTRL + SHIFT + R
```

---

# Production Update Quick Commands

For normal frontend/customization updates:

```bash
cd /var/www/Frappe

bench build --app helpdesk

bench --site pkdevops.online clear-cache

bench --site pkdevops.online clear-website-cache

bench --site pkdevops.online migrate

bench restart

sudo supervisorctl status
```

---

# Final Verification Checklist

* [ ] Ubuntu updated
* [ ] Apache installed and running
* [ ] Python 3.14 installed
* [ ] Node.js 24 installed
* [ ] Yarn installed
* [ ] MariaDB installed and running
* [ ] Redis installed and running
* [ ] wkhtmltopdf installed
* [ ] Frappe Bench installed
* [ ] Frappe v16 initialized
* [ ] `pkdevops.online` site created
* [ ] Helpdesk installed
* [ ] Telephony installed
* [ ] Supervisor configured
* [ ] Apache configured
* [ ] SSL configured
* [ ] Location DocType created
* [ ] Contact `custom_location` created
* [ ] HD Ticket `custom_location` created
* [ ] HD Ticket Template updated
* [ ] Ticket Location Server Script created
* [ ] Location-based Team Routing Server Script created
* [ ] `get_contact_customer` API created
* [ ] Contact Client Script created
* [ ] Location frontend files copied
* [ ] Helpdesk frontend built
* [ ] Cache cleared
* [ ] Migration completed
* [ ] Frappe restarted
* [ ] Supervisor processes running
* [ ] Apache running
* [ ] MariaDB running
* [ ] Redis running
* [ ] Website accessible
* [ ] Contact Location filtering working
* [ ] Ticket Location auto-fill working
* [ ] Location-based team routing working

---

# Final Result

The final system provides:

```text
Customer
   |
   +── Location A
   +── Location B
   +── Location C
          |
          v
       Contact
          |
          v
    custom_location
          |
          v
       HD Ticket
          |
          v
    Location Routing
          |
          v
      HD Team
```

The system supports:

* Customer-based Location filtering
* Contact Location assignment
* Automatic Ticket Location population
* Location-based Helpdesk team routing
* Custom Location management UI
* Direct Frappe Helpdesk v16 deployment
* Apache reverse proxy
* Supervisor process management
* MariaDB database
* Redis queues/cache
* SSL with Certbot

---

## End

Deployment root:

`/var/www/Frappe`

Customization root:

`/var/www/Frappe-Location`

Production site:

`https://pkdevops.online`
