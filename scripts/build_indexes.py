import sys
from registry import main
sys.argv.insert(1, 'build')
raise SystemExit(main())
