# Frappe Helpdesk — Location & Customer Feature — Full Build Record

Complete record of every step to add Location tracking to Helpdesk:
a sidebar Location module, Customer-filtered Location on Contacts,
auto-populated Location on Tickets, location visible on both the
agent and customer ticket detail panels, and location-based ticket
routing to teams.

This version supersedes earlier records — it includes a file
(`TicketCustomerSidebar.vue`) that was missing from the previous
package, so following this README top to bottom in one pass gets
everything working without a follow-up patch.

Replace as needed for your environment:
- Site: `<your-site>` (e.g. `desk.kingg.in`, `help.kingg.in`)
- Containers: `frappe-helpdesk-16-backend-1` / `frappe-helpdesk-16-frontend-1`
  (confirm with `docker ps` — same pattern across servers if built
  from the same compose setup, but always double-check)

---

## 0. Base deployment

Helpdesk deployed via the custom fork:
`https://github.com/KINGG777/Frappe-Helpdesk-16.git`

---

## 1. Create the `Location` doctype

`DocType → New`, name it **`Location`**, Module: `Helpdesk`

**Fields:**

| Label | Fieldname | Type | Options | Mandatory |
|---|---|---|---|---|
| Location Name | `location_name` | Data | — | Yes, Unique |
| Company | `company` | Link | `HD Customer` | Yes |

**Naming:** By fieldname, Auto Name: `field:location_name`

> ⚠️ If ERPNext is or might be installed on this site, `Location`
> collides with a core ERPNext doctype. If unsure, name yours
> `HD Location` instead and adjust every `"Location"` doctype
> reference below to match.

---

## 2. Add Location field on Contact

`https://<your-site>/app/customize-form?doctype=Contact` → Add field:

- Label: `Location`
- Type: `Link`
- Options: `Location`
- Fieldname auto-generates as **`custom_location`** — kept as-is,
  don't try to rename it. All code below expects this exact name.

---

## 3. Deploy the frontend + backend code (one pass, all files)

Unzip `helpdesk-location-full.zip` (packaged alongside this README)
onto your server, or clone `https://github.com/KINGG777/custom_helpdesk.git`
if you've pushed this same file set there.

```bash
cd ~/Frappe-Helpdesk-16
rm -rf location-deploy
unzip -o helpdesk-location-full.zip -d location-deploy
cd location-deploy

# --- Sidebar Location module ---
docker cp desk/src/components/DynamicDoctypeForm.vue            frappe-helpdesk-16-backend-1:/home/frappe/frappe-bench/apps/helpdesk/desk/src/components/DynamicDoctypeForm.vue
docker cp desk/src/pages/location                                 frappe-helpdesk-16-backend-1:/home/frappe/frappe-bench/apps/helpdesk/desk/src/pages/
docker cp desk/src/components/location                            frappe-helpdesk-16-backend-1:/home/frappe/frappe-bench/apps/helpdesk/desk/src/components/
docker cp desk/src/router/index.ts                                 frappe-helpdesk-16-backend-1:/home/frappe/frappe-bench/apps/helpdesk/desk/src/router/index.ts
docker cp desk/src/components/layouts/layoutSettings.ts            frappe-helpdesk-16-backend-1:/home/frappe/frappe-bench/apps/helpdesk/desk/src/components/layouts/layoutSettings.ts

# --- Contact Location field (create/edit popups) ---
docker cp desk/src/components/contact/NewContactDialog.vue        frappe-helpdesk-16-backend-1:/home/frappe/frappe-bench/apps/helpdesk/desk/src/components/contact/NewContactDialog.vue
docker cp desk/src/components/contact/EditContactDialog.vue       frappe-helpdesk-16-backend-1:/home/frappe/frappe-bench/apps/helpdesk/desk/src/components/contact/EditContactDialog.vue
docker cp desk/src/composables/contact.ts                          frappe-helpdesk-16-backend-1:/home/frappe/frappe-bench/apps/helpdesk/desk/src/composables/contact.ts
docker cp desk/src/types.ts                                        frappe-helpdesk-16-backend-1:/home/frappe/frappe-bench/apps/helpdesk/desk/src/types.ts
docker cp desk/src/types/doctypes.ts                                frappe-helpdesk-16-backend-1:/home/frappe/frappe-bench/apps/helpdesk/desk/src/types/doctypes.ts
docker cp helpdesk/api/contact.py                                    frappe-helpdesk-16-backend-1:/home/frappe/frappe-bench/apps/helpdesk/helpdesk/api/contact.py

# --- Ticket detail panel: Customer + Location always shown to the
#     employee/customer, independent of the "Hide from customer"
#     template flag (that flag only affects the creation form) ---
docker cp desk/src/components/ticket/TicketCustomerSidebar.vue    frappe-helpdesk-16-backend-1:/home/frappe/frappe-bench/apps/helpdesk/desk/src/components/ticket/TicketCustomerSidebar.vue

# --- Generic list-view fix: makes the Locations list (and any other
#     custom doctype list) load without crashing ---
docker cp helpdesk/api/doc.py                                       frappe-helpdesk-16-backend-1:/home/frappe/frappe-bench/apps/helpdesk/helpdesk/api/doc.py

# --- Rebuild frontend assets ---
docker exec frappe-helpdesk-16-backend-1 bash -c "cd /home/frappe/frappe-bench && bench build --app helpdesk"

# --- Sync built assets to the frontend container ---
# apps/ is baked per-container, NOT a shared volume — frontend serves
# /assets/ directly off its own disk, so it needs its own copy.
# Always wipe the host staging folder first: reusing it between runs
# causes Docker to nest the new copy inside the old one instead of
# replacing it (symptom: CSS updates fine, JS still 404s, or vice
# versa).
rm -rf /tmp/hd-desk-assets /tmp/hd-index.html
docker cp frappe-helpdesk-16-backend-1:/home/frappe/frappe-bench/apps/helpdesk/helpdesk/public/desk /tmp/hd-desk-assets
docker exec frappe-helpdesk-16-frontend-1 rm -rf /home/frappe/frappe-bench/apps/helpdesk/helpdesk/public/desk
docker cp /tmp/hd-desk-assets frappe-helpdesk-16-frontend-1:/home/frappe/frappe-bench/apps/helpdesk/helpdesk/public/desk
docker cp frappe-helpdesk-16-backend-1:/home/frappe/frappe-bench/apps/helpdesk/helpdesk/www/helpdesk/index.html /tmp/hd-index.html
docker cp /tmp/hd-index.html frappe-helpdesk-16-frontend-1:/home/frappe/frappe-bench/apps/helpdesk/helpdesk/www/helpdesk/index.html

# --- Restart and clear cache ---
docker restart frappe-helpdesk-16-backend-1
docker restart frappe-helpdesk-16-frontend-1
docker exec frappe-helpdesk-16-backend-1 bash -c "bench --site <your-site> clear-cache"
```

Then hard-refresh the browser: DevTools → Network tab → check
**Disable cache** → `Ctrl+Shift+R`.

**Result of this section:**
- Sidebar shows "Locations" below Contacts, with a metadata-driven
  Create/Edit form — add/remove/reorder fields on the `Location`
  doctype later and these forms pick it up automatically, no
  redeploy needed
- Contact create/edit popups show a Location field below Customer,
  filtered to only that customer's locations
- Employee/customer ticket detail panel will show Customer +
  Location once §5–§6 below are also done (this file alone doesn't
  populate the data, just displays it)

---

## 4. Test data

- Create at least one dummy `HD Customer`
- Create a couple of dummy `Location` records against that customer
- Invite a test portal user, and **while creating the invite, set
  both Customer and Location**
- After the invite is accepted, open the Contact record and confirm
  the Location field is actually attached (worth explicitly
  checking — a Custom Field or template misconfiguration fails
  silently, not loudly)

---

## 5. Add Location to HD Ticket

`https://<your-site>/app/customize-form?doctype=HD Ticket` → Add field:

- Label: `Location`
- Type: `Link`
- Options: `Location`
- Fieldname: `custom_location`
- **Read Only:** checked (this is auto-derived, never manually set)

---

## 6. Add the field to the Ticket Type template

`https://<your-site>/app/hd-ticket-template` → open the active
template → Fields child table → Add Row → Field (fieldname):
`custom_location` → position directly after `customer`.

This is what makes Location show up on the **agent/admin ticket
detail panel**, right below Customer.

> The customer-portal panel is different: since §3 deployed
> `TicketCustomerSidebar.vue`, Customer + Location always show there
> regardless of this template's "Hide from customer" flag. That flag
> now only controls whether they're **asked for on the new-ticket
> creation form** — check "Hide from customer" on both the
> `customer` and `custom_location` rows if you don't want the
> employee prompted for them when raising a ticket (recommended,
> since both are auto-derived).

---

## 7. Server Scripts

All created via `https://<your-site>/app/server-script/new`.

### 7.1 — Auto-fill ticket Location from contact

Keeps the ticket's `custom_location` in sync with whatever Location
is set on the raising contact. **Create this one first** — §7.2 and
the ticket detail panels depend on it.

```
Name: Ticket-Field
Script Type: DocType Event
Reference Document Type: HD Ticket
DocType Event: Before Save
```

```python
if doc.contact:
    doc.custom_location = frappe.db.get_value("Contact", doc.contact, "custom_location")
```

> ⚠️ **Editor gotcha:** the Server Script code box has been observed
> to flatten pasted multi-line code onto a single line, producing an
> invalid `if x: y if z: w` mash-up with no syntax error until you
> hit Save. If pasting multi-line code fails or looks wrong
> afterward, retype it manually pressing Enter between lines, or use
> this single-line-safe form instead:
> ```python
> doc.custom_location = frappe.db.get_value("Contact", doc.contact, "custom_location") if doc.contact else None
> ```
> Always re-open the script after saving to confirm it genuinely
> shows multiple lines, not one run-together line.
>
> If Location still doesn't populate after this is saved and
> "Enabled": clear cache and restart the containers that run this
> script (`bench --site <your-site> clear-cache`, then
> `docker restart` on `backend`, `queue-short`, `queue-long`) —
> newly created Server Scripts aren't always picked up by an
> already-running worker process until it's restarted.

### 7.2 — Location-based team routing (optional)

Auto-assigns a ticket's Team based on the contact's Location, so
tickets from a given customer site route straight to the right team.

```
Name: team-selection
Script Type: DocType Event
Reference Document Type: HD Ticket
DocType Event: Before Save
```

```python
if doc.contact:
    location = frappe.db.get_value("Contact", doc.contact, "custom_location")

    if location == "cust-1-loc-1":
        doc.agent_group = "Customer-1-Loc-1"

    elif location == "cust-1-loc-2":
        doc.agent_group = "Customer-1-Loc-2"
```

Extend the `if`/`elif` chain with one line per Location → Team
mapping as more locations/teams are added. It's fine to have this
as a second, separate Server Script alongside 7.1 — both are
"Before Save" on "HD Ticket" and both will run.

### 7.3 — `get_contact_customer` API

Used by the Contact form's Client Script (§8) to look up which
customer + locations a contact belongs to, for the raw Desk Contact
form's Location filtering.

```
Name: (your choice)
Script Type: API
API Method: get_contact_customer
```

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

Data relationship this relies on:

```
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

---

## 8. Client Script

`https://<your-site>/app/client-script/new`

```
DocType: Contact
Apply To: Form
```

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
            return { filters: { name: ["in", locations] } };
        });

    } catch (error) {
        console.error(error);
        frm.set_query("custom_location", function () {
            return { filters: { name: "" } };
        });
    }
}
```

**Effect:** on the raw Desk Contact form (`/desk/contact/...`, the
admin form — separate from the Helpdesk portal's own Vue dialogs),
the Location dropdown only offers locations belonging to that
contact's customer.

---

## Full picture — where each piece takes effect

| Surface | Mechanism |
|---|---|
| Sidebar → Locations (list/create/edit) | `DynamicDoctypeForm.vue` + Location doctype metadata |
| Helpdesk portal → Create/Edit Contact popup | `NewContactDialog.vue` / `EditContactDialog.vue`, filtered via `Link` component's `filters` prop |
| Raw Desk Contact form (`/desk/contact/...`) | Client Script `set_location_filter` + Server Script `get_contact_customer` (§7.3, §8) |
| Ticket's Location field auto-populates | Server Script "Ticket-Field" (§7.1) |
| Ticket's Team, based on Location | Server Script "team-selection" (§7.2) |
| Agent/admin/manager ticket detail panel | HD Ticket Template field config (§6) — no code change needed |
| Employee/customer ticket detail panel | `TicketCustomerSidebar.vue` (§3) — always shows Customer + Location, independent of the template's "Hide from customer" flag |
| Employee's *new ticket* creation form | HD Ticket Template's "Hide from customer" flag on `customer`/`custom_location` rows (§6) |

---

## Verification checklist

- [ ] Location doctype created, Company field mandatory
- [ ] `custom_location` exists on Contact (verify via Customize Form,
      not just visually in a form)
- [ ] Sidebar Locations works: create/edit/list, Company gates
      Location Name until filled
- [ ] Contact create/edit popups filter Location by selected Customer
- [ ] Raw Desk Contact form also filters Location by customer
- [ ] `custom_location` exists on HD Ticket, Read Only
- [ ] Ticket Type template includes `custom_location` after
      `customer`, both marked "Hide from customer" if you don't want
      them asked at ticket creation
- [ ] New ticket created by a portal contact with a Location set →
      ticket's Location auto-populates (check Error Log if it
      doesn't)
- [ ] Employee raising a new ticket is **not** asked for Customer/Location
- [ ] Employee opening an existing ticket's details **does** see
      Customer + Location
- [ ] Agent/admin ticket detail panel shows Location below Customer
- [ ] Location-to-team routing fires correctly for known location
      values in the `team-selection` script (if used)

---

## Common errors and what they mean

| Symptom | Cause | Fix |
|---|---|---|
| Blank white page, JS/CSS 404 in DevTools Network tab | Built assets weren't synced to the `frontend` container | Re-run the asset sync steps in §3 |
| CSS loads (200) but JS still 404s after a resync | `/tmp/hd-desk-assets` already existed from a previous run, causing a nested directory copy | `rm -rf /tmp/hd-desk-assets /tmp/hd-index.html` before every resync |
| Location field visible but never saves, no error shown | Custom Field genuinely doesn't exist on `Contact`/`HD Ticket` yet | Complete §2/§5 fully, reload to verify |
| `AttributeError: '...' object has no attribute 'location'`, 500 on save | Code expects fieldname `custom_location` — check it wasn't accidentally renamed | Re-check §2/§5, field name must be `custom_location` |
| Server Script saved and Enabled, but nothing happens, no error | Newly created Server Scripts aren't always picked up by already-running worker processes | `bench --site <your-site> clear-cache`, then restart `backend`, `queue-short`, `queue-long` |
| Server Script silently does nothing after a multi-line paste | Code editor flattened the paste onto one line | Retype manually, or use the single-line-safe form (see §7.1) |
| Employee sees Customer/Location on the *creation* form even after checking "Hide from customer" | §3's `TicketCustomerSidebar.vue` deploy is missing | Re-run §3, specifically the `TicketCustomerSidebar.vue` docker cp step |
| `docker cp` commands fail with `lstat: no such file or directory` | The zip was never actually unzipped, or an empty stale folder was there already | `rm -rf location-deploy && unzip -o helpdesk-location-full.zip -d location-deploy` |

---

## Notes on permanence

Everything under §3 (docker cp'd Vue/Python files) is a **fast
preview deploy** — it lives in the running container's writable
layer and is lost on container recreate, image rebuild, or host
reboot. For a permanent fix: push these files to a fork of
`frappe/helpdesk` (or the `custom_helpdesk` repo), update `apps.json`
to point at it, rebuild the image with `docker build --no-cache`, and
`docker compose up -d --force-recreate`.

Everything under §7 and §8 (Server Scripts, Client Script) lives in
the **database**, not in the container filesystem — these survive
container recreates and image rebuilds automatically, no redeploy
ever needed for changes to them.
