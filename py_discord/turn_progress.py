from discord import Embed, Colour

from py_base import ari_enum
from py_base.dbmanager import DatabaseManager
from py_system.tableobj import Deployment, Building, Resource
from py_system.systemobj import SystemBuilding





def building_progress(database: DatabaseManager, building_id: int) -> Embed:
    # 모든 건물이 생산을 실행
    # TODO 코드 작성

    deployment_row_list = database.fetch_many(Deployment.get_table_name(), building_id=building_id)
    deployment_list = Deployment.from_data_iter(deployment_row_list)
    # 건물과 대원, 가축 불러오기
    building = Building.from_database(database, id=building_id)
    deployed_crews = building.get_deployed_crews(deployment_list)
    deployed_livestocks = building.get_deployed_livestocks(deployment_list)
    
    sys_building = SystemBuilding.from_building(building)
    production_recipe = sys_building.get_production_recipe()
    
    result_embed = Embed(
        title = f"**{building.name}**({building.category.express()}) 활동 보고",
        colour = Colour.yellow()
    )
    
    # 완성되지 않은 건물의 경우
    if not sys_building.is_built():
        # 건물에 배치된 대원 불러오기
        for crew in deployed_crews:
            # 대원마다 건축 주사위 굴리기
            construction_exp = crew.get_experience(ari_enum.WorkCategory.CONSTRUCTION)
            construction_dice = construction_exp.get_labor_dice()
            construction_dice.roll()
            
            sys_building.apply_production(construction_dice.last_roll)

            result_embed.add_field(
                name=f"건축 노동원: {crew.name}",
                value=f"주사위 굴림: {construction_dice.last_roll}\n건축 진척: {sys_building.get_construction_progress()} / {sys_building.required_dice_cost}"
            )
        
        sys_building.push()
    
    # 건물에 배치된 노동원마다 실행
    for labor in deployed_crews + deployed_livestocks:
        # 자원 소모
        embed_value_list = [f"- 배치 노동원: {labor.name}", f"- 노동력: {labor.labor}"]
        for consume_resource in production_recipe.consume:
            
            r_data = database.fetch(Resource.__name__, faction_id=building.faction_id, category=consume_resource.category)
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
    for crew in deployed_crews:
        for produce_resource in sys_building.produce_resource_by_crew(
            database,
            crew
        ):
            result_embed.add_field(
                name=f"{produce_resource.category.express()}",
                value=f"- 배치 노동원: {crew.name}\n- 노동력: {crew.labor}\n- 생산량: **{produce_resource.amount}**"
            )
            produce_resource.push()
            
    for livestock in deployed_livestocks:
        for produce_resource in sys_building.produce_resource_by_livestock(
            database,
            livestock
        ):
            result_embed.add_field(
                name=f"{produce_resource.category.express()}",
                value=f"- 배치 가축: {livestock.name}\n- 노동력: {livestock.labor}\n- 생산량: **{produce_resource.amount}**"
            )
            produce_resource.push()
    
    return result_embed

