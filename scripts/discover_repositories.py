import sys
from registry import main
sys.argv.insert(1, 'discover')
raise SystemExit(main())
