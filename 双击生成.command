#!/bin/bash
cd `dirname $0`

echo '#!/bin/bash' > 双击上传.command
echo 'cd `dirname $0`' >> 双击上传.command
echo "python3 $(pwd)/sftp.py" >> 双击上传.command
echo 'read' >> 双击上传.command
chmod +x 双击上传.command

# read