from discord import Embed, Colour

from py_base import ari_enum
from py_base.dbmanager import DatabaseManager
from py_system.tableobj import Facility
from py_system.tableobj import Deployment, Resource
from py_system.facility import facility_to_concrete_facility




def facility_progress(database: DatabaseManager, facility_id: int) -> Embed:
    # 모든 시설이 생산을 실행
    # TODO 코드 작성

    deployment_row_list = database.fetch_many(Deployment.table_name, facility_id=facility_id)
    deployment_list = Deployment.from_data_iter(deployment_row_list, database)
    
    # 시설과 대원, 가축 불러오기
    facility = Facility.from_database(database, id=facility_id)
    facility = facility_to_concrete_facility(facility)
    deployed_crews = facility.get_deployed_crews(deployment_list)
    deployed_livestocks = facility.get_deployed_livestocks(deployment_list)
    
    production_recipe = facility.get_production_recipe()
    
    result_embed = Embed(
        title = f"**{facility.name}**({facility.category.express()}) 활동 보고",
        colour = Colour.yellow()
    )
    
    # 완성되지 않은 시설의 경우
    if not facility.is_built():
        # 시설에 배치된 대원 불러오기
        for sys_worker in deployed_crews + deployed_livestocks:
            # 대원마다 건축 주사위 굴리기
            # TODO
            construction_exp = sys_worker.get_experience(ari_enum.WorkCategory.CONSTRUCTION)
            exp_level = sys_worker.get_experience_level(construction_exp)
            
            facility.apply_production(sys_worker.efficiency + exp_level)

            result_embed.add_field(
                name=f"건축 노동원: {sys_worker.name}",
                value=f"진척 추가: {sys_worker.efficiency + exp_level}\n건축 진척: {facility.construction_progress} / {facility.required_dice_cost}"
            )
        
        facility.push()
    
    # 시설에 배치된 노동원마다 실행
    for sys_worker in deployed_crews + deployed_livestocks:
        # 자원 소모
        embed_value_list = [f"- 배치 노동원: {sys_worker.name}", f"- 노동력: {sys_worker.efficiency}"]
        for consume_resource in production_recipe.consume:
            
            r_data = database.fetch(Resource.table_name, faction_id=facility.faction_id, category=consume_resource.category)
            r = Resource.from_data(r_data)
            
            if r < consume_resource:
                embed_value_list.append("자원이 부족해 생산을 진행할 수 없습니다.")
                result_embed.add_field(
                    name=f"자원 부족: {consume_resource.category.express()}",
                    value="\n".join(embed_value_list)
                )
                continue
            else:
                r.amount -= consume_resource.amount
                embed_value_list.append(f"- 소모량: {consume_resource.amount}")
                result_embed.add_field(
                    name=f"{consume_resource.category.express()}",
                    value="\n".join(embed_value_list)
                )
                r.push()
        
    # 자원 생산
    for worker in deployed_crews + deployed_livestocks:
        for produce_resource in facility.produce_resource_by_worker(
            database,
            worker
        ):
            result_embed.add_field(
                name=f"{produce_resource.category.express()}",
                value=f"- 배치 노동원: {worker.name}({worker.category.express()})\n- 노동력: {worker.efficiency}\n- 생산량: **{produce_resource.amount}**"
            )
            produce_resource.push()
    
    return result_embed

