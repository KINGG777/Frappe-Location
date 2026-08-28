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
