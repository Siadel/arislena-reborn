from py_system.tableobj import Territory

t = Territory(name="테스트")

print(t.get_column_names(), t.get_data_tuple())