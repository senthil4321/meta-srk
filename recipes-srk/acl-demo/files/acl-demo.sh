#!/bin/bash
# ACL (Access Control Lists) Demonstration Script
# Shows how to use extended file permissions with setfacl and getfacl

set -e

echo "======================================"
echo "ACL (Access Control Lists) Demo"
echo "======================================"
echo

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_section() {
    echo -e "${BLUE}==== $1 ====${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Create demo directory
DEMO_DIR="/tmp/acl-demo"
rm -rf $DEMO_DIR
mkdir -p $DEMO_DIR
cd $DEMO_DIR

print_section "1. Standard Unix Permissions vs ACLs"
echo "Creating test file..."
echo "This is a test file for ACL demonstration" > testfile.txt
chmod 640 testfile.txt
print_success "Created testfile.txt with permissions 640 (rw-r----)"

echo
echo "Standard permissions:"
ls -l testfile.txt
echo
print_info "Standard Unix permissions only allow: owner, group, others"
print_info "ACLs allow fine-grained permissions for specific users/groups"

echo
print_section "2. Viewing ACLs"
echo "Current ACLs on testfile.txt:"
getfacl testfile.txt
echo

print_section "3. Setting ACLs for Specific Users"
print_info "Granting 'srk' user read and write access..."
setfacl -m u:srk:rw testfile.txt
print_success "ACL set for user 'srk'"

echo
echo "Updated permissions:"
ls -l testfile.txt
echo "(Notice the '+' symbol indicating ACLs are present)"

echo
echo "Current ACLs:"
getfacl testfile.txt
echo

print_section "4. Setting ACLs for Specific Groups"
echo "Creating group directory..."
mkdir group-shared
chmod 750 group-shared
print_info "Granting 'users' group read and execute access..."
setfacl -m g:users:rx group-shared
print_success "ACL set for group 'users'"

echo
echo "Directory ACLs:"
getfacl group-shared
echo

print_section "5. Default ACLs (Inherited by New Files)"
print_info "Setting default ACLs on directory..."
setfacl -d -m u:srk:rw group-shared
setfacl -d -m g:users:r group-shared
print_success "Default ACLs set"

echo
echo "Creating a new file in the directory..."
echo "Test content" > group-shared/newfile.txt

echo
echo "New file inherits ACLs:"
getfacl group-shared/newfile.txt
echo

print_section "6. Multiple User ACLs"
echo "Creating multi-user file..."
echo "Shared document" > document.txt
chmod 600 document.txt

print_info "Adding ACLs for multiple users..."
setfacl -m u:srk:rw document.txt
setfacl -m u:capuser:r document.txt
print_success "Multiple user ACLs set"

echo
echo "ACLs for document.txt:"
getfacl document.txt
echo

print_section "7. Removing ACLs"
echo "Creating file to demonstrate ACL removal..."
echo "Temporary file" > temp.txt
setfacl -m u:srk:rw temp.txt

echo "Before removal:"
getfacl temp.txt
echo

print_info "Removing ACL for user 'srk'..."
setfacl -x u:srk temp.txt
print_success "ACL removed"

echo
echo "After removal:"
getfacl temp.txt
echo

print_section "8. Removing All ACLs"
print_info "Removing all ACLs from temp.txt..."
setfacl -b temp.txt
print_success "All ACLs removed"

echo
echo "After complete removal:"
getfacl temp.txt
echo

print_section "9. Copying ACLs"
echo "Creating source and destination files..."
echo "Source" > source.txt
echo "Destination" > dest.txt
setfacl -m u:srk:rw source.txt
setfacl -m u:capuser:r source.txt

echo
echo "Source ACLs:"
getfacl source.txt
echo

print_info "Copying ACLs from source to destination..."
getfacl source.txt | setfacl --set-file=- dest.txt
print_success "ACLs copied"

echo
echo "Destination ACLs:"
getfacl dest.txt
echo

print_section "10. Effective Permissions"
echo "Creating file with conflicting permissions..."
echo "Test file" > effective.txt
chmod 640 effective.txt
setfacl -m u:srk:rwx effective.txt

echo
echo "ACLs for effective.txt:"
getfacl effective.txt
echo
print_info "The 'mask' entry limits the maximum permissions"
print_info "Even though srk has rwx in ACL, effective rights may be limited by mask"
echo

print_section "11. Recursive ACL Setting"
echo "Creating directory tree..."
mkdir -p recursive-test/sub1/sub2
touch recursive-test/file1.txt
touch recursive-test/sub1/file2.txt
touch recursive-test/sub1/sub2/file3.txt

print_info "Setting ACLs recursively..."
setfacl -R -m u:srk:rx recursive-test
print_success "Recursive ACLs set"

echo
echo "Checking ACLs on nested file:"
getfacl recursive-test/sub1/sub2/file3.txt
echo

print_section "12. Backup and Restore ACLs"
print_info "Backing up ACLs for the entire demo directory..."
getfacl -R . > /tmp/acl-backup.txt
print_success "ACLs backed up to /tmp/acl-backup.txt"

echo
echo "First few lines of backup:"
head -20 /tmp/acl-backup.txt
echo "..."
echo

print_info "To restore ACLs, use: setfacl --restore=/tmp/acl-backup.txt"
echo

print_section "13. Practical Use Cases"
cat <<EOF

${GREEN}Common ACL Use Cases:${NC}

1. ${YELLOW}Shared Project Directory:${NC}
   - Allow specific users to collaborate without group membership
   - setfacl -d -m u:developer1:rwx /project/shared

2. ${YELLOW}Log File Access:${NC}
   - Grant read access to monitoring tools without changing ownership
   - setfacl -m u:monitor:r /var/log/app.log

3. ${YELLOW}Web Content:${NC}
   - Allow web server and developers to access files
   - setfacl -R -m u:www-data:rx /var/www/html

4. ${YELLOW}Temporary Access:${NC}
   - Grant temporary access to a contractor
   - setfacl -m u:contractor:rw /project/docs

5. ${YELLOW}Granular Security:${NC}
   - Different permissions for different users on same file
   - setfacl -m u:viewer:r -m u:editor:rw -m u:admin:rwx file.txt

EOF

print_section "Summary"
cat <<EOF

${GREEN}Key ACL Commands:${NC}

- getfacl <file>              : View ACLs
- setfacl -m u:user:perms <file>  : Modify user ACL
- setfacl -m g:group:perms <file> : Modify group ACL
- setfacl -x u:user <file>    : Remove user ACL
- setfacl -b <file>           : Remove all ACLs
- setfacl -R -m ...           : Recursive ACL setting
- setfacl -d -m ...           : Set default ACLs

${GREEN}Permission Letters:${NC}
- r : read
- w : write
- x : execute
- - : no permission

${BLUE}Demo files created in: $DEMO_DIR${NC}
${BLUE}ACL backup saved to: /tmp/acl-backup.txt${NC}

EOF

print_success "ACL demonstration complete!"
echo
echo "You can explore the files in $DEMO_DIR"
echo "Run 'getfacl <filename>' to inspect ACLs"
echo
