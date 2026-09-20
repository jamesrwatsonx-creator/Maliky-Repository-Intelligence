import sys
from registry import main
sys.argv.insert(1, 'ingest')
raise SystemExit(main())
