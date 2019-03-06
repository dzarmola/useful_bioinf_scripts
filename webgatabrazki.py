"""Takes all .png files from the specified folder and outputs a bootstrap based responsive html"""
import sys,glob,ntpath

COLUMNS = 2

_index_template = """
<!DOCTYPE html>
<html lang="en">
    <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <title>Agata's awesome plots</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
    </head>
    <body>
    {}
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
    </body>
</html>"""

_div_e = """</div>"""
_row_s = """<div class="row">"""
_col_s = """<div class="col-md-{}">"""
_img = """<img src="{}" class="img-responsive thumbnail" style='width:100%;'/>"""

def save(savename,page):
    with open(savename,"w",0) as out:
        out.write(page)

def make_page(files,save_name="",colnum=COLUMNS):
    row_num = len(files)/3 + (len(files)/3. > len(files)/3)
    col_width = 12/colnum
    rows = []
    for row in xrange(row_num):
        r = _row_s
        for c in xrange(colnum):
            r += _col_s.format(col_width)
            f = ntpath.basename(files.pop(0))
            r+=_img.format(f)
            r += _div_e
            if not files:
                break
        r+=_div_e
        rows.append(r)
    #with open("index_template.html") as template:
    page = _index_template.format("\n".join(rows))
    #print page
    if save_name:
        save(save_name, page)



if __name__ == "__main__":
    dir = sys.argv[1]
    print "Will take images from {}".format(dir)
    files = glob.glob("{}/*.png".format(dir)) # znajduje wszystkie png w katalogu, lista
    make_page(files,save_name="{}/plots.html".format(dir))