import sys
import os
import datetime
import MySQLdb as mysql

sys.path.append(os.getcwd())
from utils import helper
from utils import history
from utils import version
from utils.cache import Cache

HOST, USER, PASSWORD, DB = helper.mysql_settings()

class DataStats:
  def __init__(self):
    cache = Cache()
    if cache.has_key("/stats"):
      self.distro_count, self.package_count, self.upstream_count, self.release_count = cache.get("/stats")
    else:
      con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
      cur = con.cursor()
      
      cur.execute("SELECT COUNT(*) FROM distros;")
      self.distro_count = cur.fetchone()[0]
      
      cur.execute("SELECT COUNT(*) FROM packages;")
      self.package_count = cur.fetchone()[0]
      
      cur.execute("SELECT COUNT( DISTINCT package_id ) FROM releases WHERE repo_id IS NULL;")
      self.upstream_count = cur.fetchone()[0]
      
      cur.execute("SELECT COUNT(DISTINCT package_id, version, revision, repos.codename) FROM releases, repos WHERE releases.repo_id = repos.id;");
      self.release_count = cur.fetchone()[0]
      con.close()
      
      cache.put("/stats", (self.distro_count, self.package_count, self.upstream_count, self.release_count), [(None, None)])
  
  def __str__(self):
    result = []
    result.append("Total distros: "+str(self.distro_count))
    result.append("Total packages: "+str(self.package_count))
    result.append("Upstream Packages: "+str(self.upstream_count))
    result.append("Total releases: "+str(self.release_count))
    return "\n".join(result)

class PackageStats:
  def __init__(self,name):
    self.hist = history.PackageHistory(name)
    
    self.vt = version.VersionTree()
    
    for date in self.hist.timeline:
      self.vt.add_release(date, self.hist.timeline[date])
  
  def for_distro(self, name, branch=None, codename=None):
    dh = history.DistroHistory(name, [self.hist], branch, codename)
    downstream = dh.get_pkg(self.hist.name)
    downstream_rev = dh.get_downstream(self.hist, True)
    
    zero = datetime.timedelta()
    diffs = []
    for date in downstream:
      diff = date-self.vt.get_date(downstream[date])
      if diff >= zero:
        diffs.append(diff)
    
    results = {"name": dh.name,
                "branch": dh.branch,
                "color": dh.color,
                "current": downstream[-1][1],
                "mean_lag": None,
                "min_lag": None,
                "max_lag": None,
                "lag": None,
                "rel_count": len(downstream),
                "mean_rev_count": 0}
    
    if len(diffs)>0:
      results["mean_lag"] = reduce(lambda x,y: x+y,diffs,zero)/len(diffs)
      results["min_lag"] = min(diffs)
      results["max_lag"] = max(diffs)
      results["lag"] = dh.timeline[-1][1]
      results["mean_rev_count"] = float(len(downstream_rev))/len(downstream)
    return results
    
if __name__=="__main__":
  s = DataStats()
  print s
  
  ps = PackageStats("gcc")
  print ps.for_distro("ubuntu","current")
