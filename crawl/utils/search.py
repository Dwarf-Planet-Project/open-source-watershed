import MySQLdb as mysql
import sys
import os
import datetime

sys.path.append(os.getcwd())
from utils import helper
from utils.history import PackageHistory

HOST, USER, PASSWORD, DB = helper.mysql_settings()

class Search:
  def __init__(self, search, basic=False):
    self.search = search
    con = mysql.connect(host=HOST,user=USER,passwd=PASSWORD,db=DB)
    cur = con.cursor()
    
    cur.execute("SELECT name, description FROM packages WHERE name LIKE %s ORDER BY LENGTH(name) ASC, name",("%"+search+"%",))
    self.results = []
    for row in cur:
      if basic:
        self.results.append((row[0], row[1]))
      else:
        self.results.append((row[0], PackageHistory(row[0])))
    con.close()
  
  def __str__(self):
    result = []
    for search,history in self.results:
      line = [search, history.name, history.description, str(history.timeline[-1][1])]
      if history.ish:
        line[-1] += "*"
      if line[0]==line[1]:
        line[1] = "-"
      result.append(" ".join(line))
    return "\n".join(result)

if __name__=="__main__":
  if len(sys.argv)>1:
    for search in sys.argv[1:]:
      results = Search(search)
      print results
  else:
    results = Search("inkscape")
    print results
