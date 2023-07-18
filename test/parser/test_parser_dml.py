# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from src.common.utils import Utils
from src.parser.mysql_parser import parser as mysql_parser
from src.parser.mysql_parser import lexer as mysql_lexer
from src.parser.oceanbase_parser import lexer as oceanbase_lexer
from src.parser.oceanbase_parser import parser as oceanbase_parser
from src.parser.tree.expression import *
from src.parser.tree.statement import *


class MyTestCase(unittest.TestCase):

    def test_and_in_update(self):
        sql = """
        update foo set t1 = '1' and t2 = '2' where t3 = '3'
        """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

    def test_update_1(self):
        result = oceanbase_parser.parse(
            """
            update jss_alarm_def  set  scope_id = 5,         
            alarm_name = 'sparkmeta-jss同步刷新任务告警',         
            create_operator = '0005292026',
            is_delete = 0,gmt_modify = '2019-08-13 17:11:56.979'
            WHERE alarm_id = 2000003
            """
        )
        assert isinstance(result, Statement)

    def test_union_and_union_all(self):
        result = oceanbase_parser.parse("""
        select a from b union select a from b
        """)
        assert isinstance(result.query_body, Union)
        assert not result.query_body.all

        result = oceanbase_parser.parse("""
                select a from b union all select a from b
                """)
        assert isinstance(result.query_body, Union)
        assert result.query_body.all

    def test_update_set(self):
        result = oceanbase_parser.parse(
            """
            UPDATE t set a = 1, b = 2 WHERE c = 3
            """
        )
        assert isinstance(result.set_list, list)
        assert isinstance(result.table, list)
        assert isinstance(result.where, ComparisonExpression)

    # def test_in_vector(self):
    #     result = oceanbase_parser.parse("""
    #     update t set a = 1, b = 2 where (c,d) in ((2,3),(4,5))
    #     """)
    #     print()

    def test_limit_question_mark(self):
        result = oceanbase_parser.parse("""
        SELECT * FROM `antinvoice93`.einv_base_info WHERE einv_source = ? ORDER BY gmt_create DESC LIMIT ?
        """)
        assert result.query_body.limit == '?'

    def test_subquery_limit(self):
        result = oceanbase_parser.parse("""
        SELECT COUNT(*) FROM ( SELECT * FROM customs_script_match_history LIMIT ? ) a
        """)
        assert isinstance(result, Statement)

    def test_current_timestamp(self):
        result = oceanbase_parser.parse("""
SELECT device_id, msg_id, short_msg_key, third_msg_id, mission_id , mission_coe, app_id, payload, template_code, business , ruleset_id, strategy, principal_id, tag, priority , expire_time, gmt_create, status, uriextinfo, sub_templates , immediate_product_version, biz_id, immediate_language_type FROM pushcore_msg WHERE device_id = ? AND principal_id = ? AND status = ? AND expire_time > current_timestamp()
        """)
        assert isinstance(result, Statement)

    def test_select_for_update(self):
        result = oceanbase_parser.parse("""
SELECT id, gmt_create, gmt_modified, match_id, match_record_id , user_id, complete_status, notice_push_status, result_push_status, reward_status , join_cost, reward, odps_reward, step_number, gmt_complete , gmt_send_reward, match_type, join_stat_bill_id, complete_stat_bill_id, ext_info FROM sports_user_match_record WHERE match_record_id IN (?) FOR UPDATE
        """)
        assert isinstance(result, Statement)
        assert result.query_body.for_update is True
        assert result.query_body.nowait_or_wait is False
        result = oceanbase_parser.parse("""
        SELECT id, gmt_create, gmt_modified, match_id, match_record_id , user_id, complete_status, notice_push_status, result_push_status, reward_status , join_cost, reward, odps_reward, step_number, gmt_complete , gmt_send_reward, match_type, join_stat_bill_id, complete_stat_bill_id, ext_info FROM sports_user_match_record WHERE match_record_id IN (?) FOR UPDATE NOWAIT
                """)
        assert isinstance(result, Statement)
        assert result.query_body.for_update is True
        assert result.query_body.nowait_or_wait is True
        result = oceanbase_parser.parse("""
                SELECT id, gmt_create, gmt_modified, match_id, match_record_id , user_id, complete_status, notice_push_status, result_push_status, reward_status , join_cost, reward, odps_reward, step_number, gmt_complete , gmt_send_reward, match_type, join_stat_bill_id, complete_stat_bill_id, ext_info FROM sports_user_match_record WHERE match_record_id IN (?) FOR UPDATE WAIT 6
                        """)
        assert isinstance(result, Statement)
        assert result.query_body.for_update is True
        assert result.query_body.nowait_or_wait is True

    def test_interval(self):
        sql = """
        SELECT biz_id, operator, MAX(gmt_create) AS gmt_create FROM log WHERE type = ? AND gmt_create > date_sub(now(), INTERVAL ? DAY) GROUP BY biz_id
        """
        result = oceanbase_parser.parse(Utils.remove_sql_text_affects_parser(sql))
        assert isinstance(result, Statement)

    def test_force_index(self):
        sql = """
        SELECT /*+read_consistency(weak) index(fund_trade_order_01 n_apply_order)*/ 
        t1.convert_out_product_id, t1.convert_out_apply_share 
        FROM fund_trade_order T1 INNER JOIN 
        ( 
        SELECT order_id, inst_apply_order_id FROM fund_trade_order FORCE INDEX (n_apply_order) 
        WHERE order_status IN (?) AND switch_flag = ? AND ta_code = ? AND scene_type <> ? 
        AND 
        (
            order_type IN (?) AND transaction_date = ? AND product_id IN (?) OR order_type = ? AND transaction_date = ? AND product_id IN (?)
        ) 
        ORDER BY inst_apply_order_id LIMIT ?, ? ) T2 WHERE t1.order_id = t2.order_id
        """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

    def test_insert(self):
        sql = """
              insert into t1 values(?,?,?)
              """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

        sql = """
              insert into t1(c1,c2,c3) values(?,?,?)
              """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

        sql = """
              insert into t1 SELECT * FROM t2
              """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

    def test_interval2(self):
        sql = """
        SELECT h.site, h.ip, h.sm_name, h.pre_group, h.nodegroup , host_name, mount, used_pct, size, used , free, m.node FROM ( SELECT host_name, mount, MAX(used_pct) AS used_pct, MAX(size) AS size, MAX(used) AS used , MIN(free) AS free, MAX(check_time) AS check_time FROM host_disk_used h FORCE INDEX (idx_ct_up_m) WHERE check_time > now() - INTERVAL ? HOUR AND mount IN (?) AND host_name NOT LIKE ? AND host_name NOT LIKE ? AND host_name NOT LIKE ? AND host_name NOT LIKE ? AND host_name NOT LIKE ? AND host_name NOT LIKE ? AND host_name NOT LIKE ? AND host_name NOT LIKE ? AND host_name NOT LIKE ? GROUP BY host_name, mount ORDER BY MAX(used) ) i, mt_armory_host h, ( SELECT ip, GROUP_CONCAT(node) AS node FROM mt_mysql_meta WHERE ip IS NOT NULL AND gmt_alive > now() - INTERVAL ? HOUR GROUP BY ip ) m WHERE i.host_name = h.hostname AND h.pre_group = ? AND m.ip = h.ip ORDER BY used"""
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

    def test_regexp(self):
        sql = """
        SELECT * FROM file_moving_serial WHERE serial_no REGEXP ?
        """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

    def test_lock_in_share_mode(self):
        sql = """
        INSERT IGNORE INTO ilimitcenter05.tp_48246_ogt_fc_lc_day (
            `id`, `tnt_inst_id`, `principal_id`, `principal_type`, `cumulate_code` , `stat_time`, `amount`, `day_count`, `reverse_amount`, 
            `reverse_count` , `max_value`, `min_value`, `cumulate_properties`, `p1`, `p2` , `p3`, `p4`, `p5`, `p6`, `p7` , `p8`, `p9`, `p10`,
            `p11`, `p12` , `p13`, `p14`, `p15`, `properties_md5`, `gmt_create` , `gmt_modified`, `currency`, `version`) SELECT `id`, `tnt_inst_id`, 
            `principal_id`, `principal_type`, `cumulate_code` , `stat_time`, `amount`, `day_count`, `reverse_amount`, `reverse_count` , 
            `max_value`, `min_value`, `cumulate_properties`, `p1`, `p2` , `p3`, `p4`, `p5`, `p6`, `p7` , `p8`, `p9`, `p10`, `p11`, `p12` , `p13`, `p14`, `p15`, 
            `properties_md5`, `gmt_create` , `gmt_modified`, `currency`, `version` 
            FROM ilimitcenter05.fc_lc_day FORCE INDEX (`PRIMARY`) 
            WHERE `id` > ? AND (`id` < ? OR `id` = ?) LOCK IN SHARE MODE
        """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = mysql_parser.parse(sql)
        assert isinstance(result, Statement)

    def test_insert_now(self):
        sql = """
        INSERT IGNORE INTO bumonitor_risk_process_context (gmt_create, gmt_modified, rowkey, context) VALUES (now(), now(), ?, ?)
        """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

    def test_distinct_2(self):
        sql = """
            /* trace_id=0b7cad2e168016361004041132631,rpc_id=0.5c88b07f.9.1 */                      SELECT /*+ index(midas_record_value idx_tenant_time) */                 DISTINCT(trace_id)             FROM                 midas_record_value where tenant='fascore' and is_expired=0  order by gmt_modified asc limit 500        
            """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

    def test_quoted(self):
        sql = "SELECT Original_artist FROM table_15383430_1 WHERE Theme = 'year'"
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)
        sql = '''SELECT Original_artist FROM table_15383430_1 WHERE Theme = "year"'''
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = mysql_parser.parse(sql)
        assert isinstance(result, Statement)

    def test_chinese_character(self):
        sql = "SELECT `净值` FROM FundTable WHERE `销售状态` = \"正常申购\""
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)
        sql = "SELECT 净值 FROM FundTable WHERE 销售状态 = \"正常申购\""
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)
        sql = '''SELECT 赎回状态a FROM FundTable WHERE 重b仓 like \"北部湾港%\"'''
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

    def test_current_date(self):
        sql = """
        select 
            t1,t2
        from 
            foo 
        where 
            t1 > (CURRENT_DATE() - INTERVAL 30 day)+'0' 
        """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

    def test_double_type(self):
        sql = """
        SELECT Winner FROM table_11621915_1 WHERE Purse > 964017.2297960471 AND Date_ds = "may 28"
        """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

    def test_union_has_order_limit(self):
        sql = """
        ( select 球员id from 球员夺冠次数 order by 冠军次数 asc limit 3 ) union ( select 球员id from 球员夺冠次数 order by 亚军次数 desc limit 5 )
        """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

    def test_order_by_has_parentheses(self):
        sql = """
SELECT channel_code , contact_number FROM customer_contact_channels WHERE active_to_date - active_from_date = (SELECT active_to_date - active_from_date FROM customer_contact_channels ORDER BY (active_to_date - active_from_date) DESC LIMIT 1)        """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

    def test_boolean_expression(self):
        sql = """
        SELECT T1.list_followers, T2.user_subscriber = 1 FROM lists AS T1 INNER JOIN lists_users AS T2 ON T1.user_id = T2.user_id AND T2.list_id = T2.list_id WHERE T2.user_id = 4208563 ORDER BY T1.list_followers DESC LIMIT 1
        """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

    def test_date_add(self):
        sql = """
        select date_format(date_format(date_add(biz_date, interval -1 day), '%y%m%d'), '%y%m%d') from t
        """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

    def test_as(self):
        sql = """
        select t2.biz_date as biz_date, f1.calculate_field / t2.calculate_field1 as d_remain_rate from ( select t1.biz_date as biz_date , count(DISTINCT if(t1.biz_date_is_visit = '1', t1.user_id, null)) as calculate_field1 from ( select * from pets_user_miaowa_galileo_visit_user_di ) t1 where t1.appname in ('AppPetWXSS', 'HelloPet') and t1.biz_date between date_format(date_sub(date_format(date_sub(curdate(), interval 1 day), '%Y%m%d'), interval 1 day), '%Y%m%d') and date_format(date_sub(curdate(), interval 1 day), '%Y%m%d') group by t1.biz_date ) t2 left join ( select date_format(date_format(date_add(t1.biz_date, interval -1 day), '%Y%m%d'), '%Y%m%d') as biz_date , count(DISTINCT if(datediff(t1.biz_date, t1.last_visit_date) = 1 and t1.biz_date_is_visit = '1', t1.user_id, null)) as calculate_field from ( select * from pets_user_miaowa_galileo_visit_user_di ) t1 where t1.appname in ('AppPetWXSS', 'HelloPet') and t1.biz_date between date_format(date_sub(date_format(date_sub(curdate(), interval 1 day), '%Y%m%d'), interval 1 day), '%Y%m%d') and date_format(date_sub(curdate(), interval 1 day), '%Y%m%d') group by date_format(date_format(date_add(t1.biz_date, interval -1 day), '%Y%m%d'), '%Y%m%d') ) f1 on t2.biz_date = f1.biz_date order by biz_date asc limit 0, 1000
        """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

    def test_single_quote_escape(self):
        sql = """
        SELECT director_id FROM movies WHERE movie_title = 'It''s Winter'
        """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

        sql = """
        SELECT director_id FROM movies WHERE movie_title = "It''s Winter"
        """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

    def test_operator(self):
        sql = """
        select         count(1)         from train_order_info where  occupy_type in              (                   ?              )                                  and order_serial_no =  ?                                 and connect_type =  ?                                     and merchant_id = ''                                 and order_state in              (                   ?              )                                 and ticket_machine_id in              (                   ?              )                                 and lock_state =  ?                                 and phone_verify_status =  ?                                 and window_no =  ?                                 and passenger_info like concat('%',concat( ?,'%'))                                 and departure_station like concat('%',concat( ?,'%'))                                 and arrival_station like concat('%',concat( ?,'%'))                                 and merchant_id =  ?                                 and createtime >=  ?                                 and createtime <=  ?                                 and gmt_booked >=  ?                                 and gmt_booked <=  ?                                 and gmt_departure >=  ?                                 and gmt_departure <=  ?                                 and train_code =  ?                                 and pay_serial_no =  ?                                 and env =  ?                                  and gmt_distribute >=  ?                                 and gmt_distribute <=  ?                                  and inquire_type in              (                   ?              )                                 and merchant_business_type =  ?                                 and ability_require &  ? =  ?
        """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

    def test_negative_number_in_limit(self):
        sql = """
            select * from foo limit 10,-10
        """
        sql = Utils.remove_sql_text_affects_parser(sql)
        result = oceanbase_parser.parse(sql)
        assert isinstance(result, Statement)

>>>>>>> 2af7bef (fix(parser):support negative number in limit" (#84))

    def test_mysql_regexp_opt(self):
        test_sqls = [
            """SELECT * FROM t WHERE a RLIKE 'hello|world'""",
            """SELECT * FROM t WHERE a REGEXP 'hello|world'""",
        ]
        for sql in test_sqls:
            sql = Utils.remove_sql_text_affects_parser(sql)
            result = mysql_parser.parse(sql, lexer=mysql_lexer.lexer)
            assert isinstance(result, Statement)

    def test_mysql_resvered_word_can_used_as_token(self):
        test_sqls = [
            """SELECT FROM FROM t""",
            """SELECT cast FROM t""",
            """SELECT end FROM t""",
            """SELECT escape FROM t""",
            """SELECT for FROM t""",
            """SELECT group FROM t""",
            """SELECT if FROM t""",
            """SELECT in FROM t""",
            """SELECT id FROM t""",
            """SELECT into FROM t""",
            """SELECT is FROM t""",
            """SELECT on FROM t""",
            """SELECT or FROM t""",
            """SELECT use FROM t""",
            """SELECT with FROM t""",
            """SELECT engine FROM t""",
        ]
        for sql in test_sqls:
            sql = Utils.remove_sql_text_affects_parser(sql)
            result = mysql_parser.parse(sql, lexer=mysql_lexer.lexer)
            assert isinstance(result, Statement)


if __name__ == "__main__":
    unittest.main()
