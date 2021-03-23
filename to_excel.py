import whois
import re


def check_ip(ip):
    r = re.findall("\d+\.\d+\.\d+\.\d+",ip)
    if r == []:
        return False
    else:
        return True
    """
    if r != []:
        return False
    else:
        return r[0]
    """


def make_xl(data,uid):
    result_dict = []
    print(len(data))
    for i in range(len(data)):
        if check_ip(data[i]) == False:
            pass
            #print(i,'was passed')
        else:
            print(i)
            tmp_addr = whois.whois(data[i])
            result_dict.append({"IP":data[i]})
            result_dict[i]["City"] = tmp_addr.city
            result_dict[i]["Country"] = tmp_addr.country
            result_dict[i]["State"] = tmp_addr.state
            result_dict[i]["Whose"] = uid
            #result_dict[i]["Email"] = tmp_addr.email
            #bug with email1-2
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
