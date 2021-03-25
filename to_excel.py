import whois
import re
from loguru import logger

#logger.add("info.json", format="{time} {level} {message}", level="INFO", rotation="5 MB", compression="zip", serialize=True)

def check_ip(ip):
    r = re.findall("\d+\.\d+\.\d+\.\d+",ip)
    if r == []:
        return False
    else:
        return True

def make_xl(data,uid):
    result_dict = []
    for i in range(len(data)):
        if check_ip(data[i]) == False:
            result_dict.append({"IP":data[i]})
            result_dict[i]["City"] = None
            result_dict[i]["Country"] = None
            result_dict[i]["State"] = None
            result_dict[i]["Whose"] = None
            #result_dict[i]["Email"] = None
            result_dict[i]["Emails"] = None
            result_dict[i]["Email1"] = None
            result_dict[i]["Email2"] = None
            result_dict[i]["Domain"] = None
            result_dict[i]["Domain1"] = None
            result_dict[i]["Domain2"] = None
            result_dict[i]["Address"] = None
            result_dict[i]["Address1"] = None
            result_dict[i]["Address2"] = None
        else:
            result_dict.append({"IP":data[i]})
            tmp_addr = whois.whois(data[i])
            result_dict[i]["City"] = tmp_addr.city
            result_dict[i]["Country"] = tmp_addr.country
            result_dict[i]["State"] = tmp_addr.state
            result_dict[i]["Whose"] = uid
            #result_dict[i]["Email"] = tmp_addr.email
            result_dict[i]["Email1"] = None
            result_dict[i]["Email2"] = None
            if type(tmp_addr.domain_name) == list:
                result_dict[i]["Domain1"] = tmp_addr.domain_name[0]
                result_dict[i]["Domain2"] = tmp_addr.domain_name[1]
            else:
                result_dict[i]["Domain"] = tmp_addr.domain_name
            if type(tmp_addr.emails) == list:
                result_dict[i]["Email1"] = tmp_addr.emails[0]
                result_dict[i]["Email2"] = tmp_addr.emails[1]
            else:
                result_dict[i]["Emails"] = tmp_addr.emails
            if type(tmp_addr.adderss) == list:
                result_dict[i]["Address1"] = tmp_addr.address[0]
                result_dict[i]["Address2"] = tmp_addr.address[1]
            else:
                result_dict[i]["Address"] = tmp_addr.address

    return result_dict
