
audit

```shell
$ oscap xccdf eval \
    --profile xccdf_org.ssgproject.content_profile_rht-ccp \
    --results ssg-rhel8-xccdf-result.xml \
    --report ssg-rhel8-report.html \
    /usr/share/xml/scap/ssg/rhel8/ssg-rhel8-ds.xml
```



```shell
$ oscap xccdf generate fix --fix-type ansible \
  --fetch-remote-resources \
  --output hardening-playbook.yml \
  --result-id xccdf_org.ssgproject.content_profile_cis_level2_server \
  scap-security-guide-0.1.73/ssg-ubuntu2204-ds.xml

$ oscap xccdf generate fix \
    --profile ospp \
    --fix-type ansible
    /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml > playbook.yml
```
