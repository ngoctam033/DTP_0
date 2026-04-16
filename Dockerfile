FROM odoo:19.0

USER root

RUN mkdir -p /mnt/extra-addons/dtp_addons /etc/odoo \
    && chown -R odoo:odoo /mnt/extra-addons /etc/odoo

WORKDIR /var/lib/odoo

USER odoo
