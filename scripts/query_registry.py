import sys
from registry import main
sys.argv.insert(1, 'query')
raise SystemExit(main())
