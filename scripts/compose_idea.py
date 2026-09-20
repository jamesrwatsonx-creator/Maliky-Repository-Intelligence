import sys
from registry import main
sys.argv.insert(1, 'compose')
raise SystemExit(main())
