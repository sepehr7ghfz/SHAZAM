#!/usr/bin/python
from libs.db_sqlite import SqliteDatabase

# get summary information
def printSummary():
  row = db.executeOne("""
    SELECT
      (SELECT COUNT(*) FROM songs) as songs_count,
      (SELECT COUNT(*) FROM fingerprints) as fingerprints_count
  """)

  msg = ' * %s: %s (%s)' % ('total','%d song(s)', '%d fingerprint(s)')
  print(msg % row)

  return row[0] # total

# get songs \w details
def printSongs():
  rows = db.executeAll("""
    SELECT
      s.id,
      s.name,
      (SELECT count(f.id) FROM fingerprints AS f WHERE f.song_fk = s.id) AS fingerprints_count
    FROM songs AS s
    ORDER BY fingerprints_count DESC
  """)

  for row in rows:
    msg = '   ** %s %s: %s' % ('id=%s','%s','%d hashes')
    print(msg % row)

# find duplicates
def printDuplicates():
  rows = db.executeAll("""
    SELECT a.song_fk, s.name, SUM(a.cnt)
    FROM (
      SELECT song_fk, COUNT(*) cnt
      FROM fingerprints
      GROUP BY hash, song_fk, offset
      HAVING cnt > 1
      ORDER BY cnt ASC
    ) a
    JOIN songs s ON s.id = a.song_fk
    GROUP BY a.song_fk
  """)

  msg = ' * duplications: %s' % '%d song(s)'
  print(msg % len(rows))

  for row in rows:
    msg = '   ** %s %s: %s' % ('id=%s','%s','%d duplicate(s)')
    print(msg % row)

# find colissions
def printColissions():
  rows = db.executeAll("""
    SELECT sum(a.n) FROM (
      SELECT
        hash,
        count(distinct song_fk) AS n
      FROM fingerprints
      GROUP BY `hash`
      ORDER BY n DESC
    ) a
  """)

  msg = ' * colissions: %s' % '%d hash(es)'
  val = 0
  if rows[0][0] is not None:
    val = rows[0]

  print(msg % val)

if __name__ == '__main__':
  db = SqliteDatabase()
  print('')

  x = printSummary()
  printSongs()
  if x: print('')

  printDuplicates()
  if x: print('')

  printColissions()

  print('\ndone')