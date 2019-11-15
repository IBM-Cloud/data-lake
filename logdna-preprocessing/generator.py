import os

def main(args):

    uri_input = args.get("uri_input")
    uri_target = args.get("uri_target")
    logDnaObject = args.get("logDna_object")

    sql = 'SELECT *, ' + \
        'date_format(from_unixtime(_source._ts / 1000, "yyyy-MM-dd HH:mm:ss"), "yyyy") AS _year, ' + \
        'dayofyear(from_unixtime(_source._ts / 1000, "yyyy-MM-dd HH:mm:ss")) AS _dayofyear, ' + \
        'date_format(from_unixtime(_source._ts / 1000, "yyyy-MM-dd HH:mm:ss"), "HH") AS _hour ' + \
        'FROM {} STORED AS JSON ' + \
        'INTO {}/ STORED AS JSON PARTITIONED BY (_year, _dayofyear, _hour)'
    return {"sql": sql.format(uri_input + "/" + logDnaObject, uri_target)}

if __name__ == '__main__':
    os.environ['__OW_IAM_NAMESPACE_API_KEY'] = "DUMMY"
    print(main({}))
