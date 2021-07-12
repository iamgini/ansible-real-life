Get Content files
  - identify files
  - read

    - name: Display the JSON file and collect data
      shell: cat {{ cve_json_file }}
      register: result  

      "{{ lookup('file','myjson.json') | from_json }}"

    - name: Save the Json data to a Variable
      set_fact:
         jsondata: "{{ result.stdout | from_json }}"      

         jsondata['*']['lsblk']


- Ansible Loops
- Extract data from json data
- Basics of custom module writing
