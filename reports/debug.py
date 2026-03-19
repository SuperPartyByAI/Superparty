import sys
sys.path.append('.')
import traceback
try:
    import agent.seo_agent.daily_report as dr
    dr.generate_report()
except Exception as e:
    print('TRACEBACK:')
    print(traceback.format_exc())
