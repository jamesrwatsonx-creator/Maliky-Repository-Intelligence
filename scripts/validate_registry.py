import sys
from registry import main
sys.argv.insert(1, 'validate')
raise SystemExit(main())
