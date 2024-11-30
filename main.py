from scripts.treeNamesRebuild import main
import os

try:
    main()
    print("运行成功")
except:
    try:
        os.system(f"rmdir testa /S/Q")
        print("清除完毕")
    except:
        print("清除失败")