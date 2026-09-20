import sys
from registry import main
sys.argv.insert(1, 'status')
raise SystemExit(main())
