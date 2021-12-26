


## Optimizing Module

Old method


```yaml
- name: Install httpd
  ansible.builtin.yum:
    name: httpd

- name: Install firewalld
  ansible.builtin.yum:
    name: firewalld

- name: Install git
  ansible.builtin.yum:
    name: git
```

or 

```yaml
- name: Install Pacakages
  ansible.builtin.yum:
    name: "{{ item }}"
    state: latest
  loop:
    - httpd
    - firewalld
    - git
    
```

Correct and efficient method

```yaml
- name: Install httpd and firewalld
  ansible.builtin.yum:
    name: 
      - httpd
      - firewalld
      - git
    state: latest
```


## Templates

```



## Optimizing Module

Old method


```yaml
- name: Install httpd
  ansible.builtin.yum:
    name: httpd

- name: Install firewalld
  ansible.builtin.yum:
    name: firewalld

- name: Install git
  ansible.builtin.yum:
    name: git
```

or 

```yaml
- name: Install Pacakages
  ansible.builtin.yum:
    name: "{{ item }}"
    state: latest
  loop:
    - httpd
    - firewalld
    - git
    
```

Correct and efficient method

```yaml
- name: Install httpd and firewalld
  ansible.builtin.yum:
    name: 
      - httpd
      - firewalld
      - git
    state: latest
```


## Template: `nginxd.conf.j2`

```
# nginx configuration for wp-test
server {
    root {{ website_root_dir }};
    index index.php index.html index.htm;
    server_name {{ website_name }}.com www.{{ website_name }}.com;
    access_log /var/log/nginx/access_{{ website_name }}-com.log;
    error_log /var/log/nginx/error_{{ website_name }}-com.log;
    location / {
        #try_files $uri $uri/ =404;
        try_files $uri $uri/ /index.php$is_args$args;
    }
    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php7.3-fpm.sock;
    }
    listen [::]:443 ssl; # managed by Certbot
    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/{{ website_name }}.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/{{ website_name }}.com/privkey.pem; # managed by Certb
ot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}
server {
    if ($host = www.{{ website_name }}.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot
    if ($host = {{ website_name }}.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot
    listen 80;
    listen [::]:80;
    server_name {{ website_name }}.com www.{{ website_name }}.com;
    return 404; # managed by Certbot
}
```

Playbook

```
---
- name: Configure the nginx Web Server
  hosts: web_servers
  become: True 
  vars:
    website_name: myawesomeblog
    website_root_dir: /var/www/myawesomeblogdata
  tasks:
    - name: Copy nginx configuration
      template:
        src: nginxd.conf.j2
        dest: /etc/nginx/sites-enabled/{{ website_name }}.conf
```        