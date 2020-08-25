"""This module manages selenium scripts backend for TutorApp"""

from time import sleep

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    NoSuchWindowException,
    ElementNotInteractableException,
    SessionNotCreatedException,
    ElementClickInterceptedException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from fileparser import parse


class BbScripts:
    """asd
    """

    def __init__(self, username, password, func=None, path=None,
                 logger=None, output=None, env=None):
        try:
            chrome_options = Options()
            prefs = {"profile.managed_default_content_settings.images": 2}
            chrome_options.add_experimental_option("prefs", prefs)
            # chrome_options.headless = True

            self.updater_flag = False

            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(2)

            if env is None:
                self.env = "unab"
            else:
                self.env = env

            self.logger = logger
            self.output = output

            self.path = path

            self.username = username
            self.password = password

            self.send_data_output("Lanzando navegador")

            self.func_dict = {
                1: self.change_role,
                2: self.disable_students,
                3: self.change_date,
                4: self.post_announcements,
                5: self.post_tutor_info,
            }

            self.url_dict = {
                "courses":
                    "https://{}.blackboard.com/webapps/blackboard/execute/courseManager"
                    "?sourceType=COURSES",
                "properties":
                    "https://{}.blackboard.com/webapps/blackboard/execute/cp/courseProperties?"
                    "dispatch=editProperties&family=cp_edit_properties&{}",
                "course_ws":
                    "http://ssb.unab.cl:9027/pls/PROD/bwwreplistados_cursos.lista_curso3?"
                    "periodo={}&nrc={}&cod_actividad=TEO",
                "user_manager":
                    "https://{}.blackboard.com/webapps/blackboard/execute/userManager?{}",
                "announcements":
                    "https://unab.blackboard.com/webapps/blackboard/execute/announcement?"
                    "method=search&editMode=true&viewChoice=2&{}&"
                    "context=course&internalHandle=cp_announcements",
                "tutor_info":
                "https://unab.blackboard.com/bbcswebdav/institution/Plan_z_matematicas/_/"
                "fichas_tutores/{}.jpg".format(username)
            }

            self.send_data_output("Entrando con credenciales proporcionadas")

            self.login()

            self.send_data_output("Ejecutando script")

            self.func_dict[func]()
        except NoSuchWindowException:
            self.send_data_output("Ventana cerrada")
        except SessionNotCreatedException:
            text = (
                "Chrome ha sido actualizado y la versión actual no es soportada por la App tutores"
                ", contactar al desarrollador para que faciliten la versión actualizada"
            )
            logger.info(text)
            output(text)
            self.updater_flag = True
        finally:
            if not self.updater_flag:
                self.driver.close()
                self.driver.quit()

    def send_data_output(self, text):
        if self.logger is None and self.output is None:
            print(text)
            return
        self.logger.info(text)
        self.output(text)
        sleep(0.1)

    def login(self):
        self.driver.get("http://{}.blackboard.com".format(self.env))

        login_btn = self.driver.find_element_by_class_name("boton2")
        login_btn.send_keys(Keys.ENTER)

        login_user = self.driver.find_element_by_id("user_id")
        login_user.send_keys(self.username)

        login_pass = self.driver.find_element_by_id("password")
        login_pass.send_keys(self.password)
        login_pass.send_keys(Keys.ENTER)

    def search_bar(self, id_to_look, value_to_look=False):
        text_box = self.driver.find_element_by_id(id_to_look)
        text_box.clear()
        if value_to_look:
            text_box.send_keys(value_to_look)
        text_box.send_keys(Keys.ENTER)

    def change_combo_box_value(self, id_to_look, value_to_set):
        combo_box = Select(self.driver.find_element_by_id(id_to_look))
        combo_box.select_by_value(value_to_set)

    def check_box_value(self, id_to_look):
        check_box = self.driver.find_element_by_id(id_to_look)
        check_box.send_keys(Keys.NULL)
        check_box.send_keys(Keys.SPACE)

    def submit_changes(self, id_to_look):
        submit = self.driver.find_element_by_id(id_to_look)
        submit.send_keys(Keys.ENTER)

    def click_text_link(self, text):
        element = self.driver.find_element_by_link_text(text)
        element.click()

    def extract_data_banner_ws(self, term, nrc):
        self.driver.get(self.url_dict["course_ws"].format(term, nrc))
        user_list = []
        try:
            row_skipper = 5
            while True:
                table_id = self.driver.find_element_by_xpath(
                    "/html/body/table[{0}]".format(row_skipper))
                rows = table_id.find_elements_by_tag_name("tr")
                for row in rows:
                    col = row.find_elements_by_tag_name("td")
                    username = col[3]
                    user_list.append(username.text)
                row_skipper += 5
        except NoSuchElementException:
            self.send_data_output(
                "Se han encontrado {} estudiantes en la lista de Banner".format(
                    len(user_list)
                )
            )
            return user_list

    def compare_bn_bb(self):
        table_id = self.driver.find_element_by_id("listContainer_databody")
        rows = table_id.find_elements_by_tag_name("tr")

        user_listbb = []
        user_disabled = []

        for row in rows:
            col1 = row.find_element_by_tag_name("th")
            # TODO try to use .text here to save 1 line
            col1 = col1.find_element_by_tag_name("span")
            cols = row.find_elements_by_tag_name("td")
            role_col = cols[4]
            course_role = role_col.find_elements_by_tag_name("span")[1]
            avl_col = cols[6]
            available_ind = avl_col.find_elements_by_tag_name("span")[1]
            username = col1.text
            if "Student" in course_role.text or "Estudiante" in course_role.text:
                if "_preview" not in username:
                    username = str(col1.text).strip()
                    user_listbb.append(username)
                    if available_ind.text == "Sí" or available_ind.text == "Yes":
                        pass
                    elif available_ind.text == "No":
                        user_disabled.append(username)
                    else:
                        self.send_data_output(
                            "Estudiante {} no tiene marca debe ser revisado".format(
                                username))
        self.send_data_output(
            "Se han encontrado {} estudiantes en la lista de Blackboard".format(
                len(user_listbb)))
        return user_listbb, user_disabled

    def list_show_all(self):
        try:
            show_all = self.driver.find_element_by_id(
                "listContainer_showAllButton")
            show_all.send_keys(Keys.ENTER)
        except NoSuchElementException:
            pass

    @staticmethod
    def disect_course_id(course_id):
        if "_" in course_id:
            (term, nrc, code) = course_id.split("_")
            return term, nrc, code, None
        else:
            (code, term, nrc, ed_me) = course_id.split(".")
            return term, nrc, code, ed_me

    @staticmethod
    def get_course_id(url):
        course_id = url[url.index("course_id="):]
        if "course_id=_1" in course_id:
            course_id = course_id[
                : course_id.index("_1", course_id.index("_1") + 2) + 2
            ]
        else:
            course_id = course_id[: course_id.index("_1") + 2]
        return course_id

    def change_role(self):
        lines = parse(self.path)
        for line in lines:
            course_name = line[0]
            user = line[1]
            role = line[2]

            self.send_data_output(
                "Cambiando rol de {} a {} en el curso {}".format(
                    user, role, course_name
                )
            )

            self.driver.get(self.url_dict["courses"].format(self.env))

            self.change_combo_box_value(
                "courseInfoSearchKeyString", "CourseId")

            self.search_bar("courseInfoSearchText", course_name)

            self.click_text_link(course_name)

            course_id = self.get_course_id(self.driver.current_url)

            self.driver.get("https://{}.blackboard.com/webapps/blackboard/execute/userManager?"
                            .format(self.env) + course_id)

            self.change_combo_box_value(
                "userInfoSearchOperatorString", "Equals")

            self.search_bar("search_text", user)

            try:
                usermenu = self.driver.find_element_by_xpath(
                    "/html/body/div[5]/div[2]/div/div/div/div/div[4]"
                    "/form/div[2]/div[3]/div/table/tbody/tr/th/span[2]/a"
                )

            except NoSuchElementException:
                usermenu = self.driver.find_element_by_xpath(
                    "/html/body/div[5]/div[2]/div/div/div/div/div[3]"
                    "/form/div[2]/div[3]/div/table/tbody/tr/th/span[2]/a"
                )

            usermenu.send_keys(Keys.ENTER)

            modify_role = self.driver.find_element_by_id(
                "cp_course_role_modify")
            modify_role.click()

            self.check_box_value(role)

            self.submit_changes("bottom_Submit")

            self.send_data_output(
                "Rol de {} cambiado a {} en el curso {} exitosamente".format(
                    user, role, course_name
                )
            )

    def disable_students(self):
        lines = parse(self.path)
        for course_id in lines:
            self.send_data_output("Procesando curso {}".format(course_id))

            term, nrc, code, ed_me = self.disect_course_id(course_id)

            user_list = self.extract_data_banner_ws(term, nrc)

            self.driver.get(self.url_dict["courses"].format(self.env))

            self.change_combo_box_value(
                "courseInfoSearchKeyString", "CourseId")

            self.search_bar("courseInfoSearchText", course_id)

            self.click_text_link(course_id)

            pk1 = self.get_course_id(self.driver.current_url)

            self.driver.get(
                self.url_dict["user_manager"].format(self.env, pk1))

            self.list_show_all()

            user_listbb, user_disabled = self.compare_bn_bb()

            list_difference = [
                item for item in user_listbb if item not in user_list]

            self.send_data_output(
                "Ajustando diferencia de {} estudiantes en Blackboard".format(
                    len(list_difference)))

            if len(user_disabled) > 0:
                self.send_data_output(
                    "{} usuarios ya se encuentran deshabilitados:\n".format(
                        len(user_disabled))
                    + ("{}\n" * len(user_disabled)).format(*user_disabled))
                list_difference = [
                    item for item in list_difference if item not in user_disabled]

            if len(list_difference) == 0:
                self.send_data_output(
                    "Curso {} completado, los usuarios ya estaban deshabilitados".format(
                        course_id))
                continue

            for user in list_difference:
                self.driver.get(
                    self.url_dict["user_manager"].format(self.env, pk1))

                self.change_combo_box_value(
                    "userInfoSearchOperatorString", "Equals")

                self.search_bar("search_text", user)

                try:
                    usermenu = self.driver.find_element_by_xpath(
                        "/html/body/div[5]/div[2]/div/div/div/div/div[4]"
                        "/form/div[2]/div[3]/div/table/tbody/tr/th/span[2]/a"
                    )

                except NoSuchElementException:
                    usermenu = self.driver.find_element_by_xpath(
                        "/html/body/div[5]/div[2]/div/div/div/div/div[3]"
                        "/form/div[2]/div[3]/div/table/tbody/tr/th/span[2]/a"
                    )

                usermenu.click()

                modify_role = self.driver.find_element_by_id(
                    "cp_course_availability")
                modify_role.click()

                self.change_combo_box_value("availableIndex", "false")

                self.submit_changes("bottom_Submit")

            self.change_combo_box_value(
                "userInfoSearchOperatorString", "NotBlank")

            self.search_bar("search_text")

            self.send_data_output(
                "Curso {} completado, {} usuarios deshabilitados:\n".format(
                    course_id, len(list_difference)
                )
                + ("{}\n" * len(list_difference)).format(*list_difference)
            )

    def change_date(self):
        lines = parse(self.path)
        for elem in lines:
            course_name = elem[0]
            if len(course_name) == 1:
                return
            value = elem[1]

            self.driver.get(self.url_dict["courses"].format(self.env))

            self.change_combo_box_value(
                "courseInfoSearchKeyString", "CourseId")

            self.search_bar("courseInfoSearchText", course_name)

            self.click_text_link(course_name)

            course_id = self.get_course_id(self.driver.current_url)

            self.driver.get(
                self.url_dict["properties"].format(self.env, course_id))

            end_date_chk = self.driver.find_element_by_id("end_duration")
            end_date_chk.send_keys(Keys.NULL)  # Focus

            if value == "Y":
                if not end_date_chk.is_selected():
                    end_date_chk.send_keys(Keys.SPACE)
            elif value == "N":
                if end_date_chk.is_selected():
                    end_date_chk.send_keys(Keys.SPACE)

            self.submit_changes("bottom_Submit")

            self.send_data_output(
                "Completado, curso {} fue marcado con {} en el cierre".format(
                    course_name, value
                )
            )

    def post_announcements(self):
        lines = parse(self.path)
        for elem in lines:
            course_name = elem[0]
            post_type = elem[1]
            subject = elem[2]
            url_txt = elem[3]
            send_immediately = elem[4]

            self.send_data_output(
                "Procesando anuncio tipo {} en {}".format(
                    post_type, course_name)
            )

            self.driver.get(self.url_dict["courses"].format(self.env))

            self.change_combo_box_value(
                "courseInfoSearchKeyString", "CourseId")

            self.search_bar("courseInfoSearchText", course_name)

            self.click_text_link(course_name)

            course_id = self.get_course_id(self.driver.current_url)

            self.driver.get(self.url_dict["announcements"].format(course_id))

            pk1 = course_id.split("=")
            pk1 = pk1[1]

            self.driver.execute_script(
                "javascript:designer_participant.toggleEditMode('javascript:"
                "Announcement.addAnnouncement()','{}','designer')".format(pk1)
            )

            subj = self.driver.find_element_by_id("subject")
            subj.send_keys(subject)

            self.driver.find_element_by_id(
                "isPermanent_true").send_keys(Keys.NULL)

            sleep(3)

            if post_type == "IMG":
                try:
                    insert_image = self.driver.find_element_by_xpath(
                        "/html/body/div[5]/div[2]/div/div/div/div/div["
                        "2]/form/div/div[2]/div/ol/li[2]/div["
                        "2]/table/tbody/tr/td/span[2]/table/tbody/tr["
                        "1]/td/div/span/div[2]/table[3]/tbody/tr/td[4]"
                    )
                    insert_image.click()
                except ElementNotInteractableException:
                    self.driver.find_element_by_id(
                        "messagetext_bb_slidercontrol"
                    ).click()
                    sleep(0.2)
                    insert_image = self.driver.find_element_by_xpath(
                        "/html/body/div[5]/div[2]/div/div/div/div/div["
                        "2]/form/div/div[2]/div/ol/li[2]/div["
                        "2]/table/tbody/tr/td/span[2]/table/tbody/tr["
                        "1]/td/div/span/div[2]/table[3]/tbody/tr/td[4]"
                    )
                    insert_image.click()
                finally:
                    self.send_data_output(
                        "Adjuntando URL de IMG en ventana emergente")
                    old_window = self.driver.window_handles[0]
                    new_window = self.driver.window_handles[1]

                    self.driver.switch_to.window(new_window)
                    img_text = self.driver.find_element_by_id(
                        "imagepackage_selectedCSFilePath"
                    )
                    img_text.send_keys(url_txt)

                    alt = self.driver.find_element_by_id("alt")
                    alt.send_keys(".")

                    title = self.driver.find_element_by_id("title")
                    title.send_keys(".")

                    insert_btn = self.driver.find_element_by_id("insert")
                    insert_btn.click()

                    self.driver.switch_to.window(old_window)
            elif post_type == "HTML":
                try:
                    insert_html = self.driver.find_element_by_xpath(
                        "/html/body/div[5]/div[2]/div/div/div/div/div["
                        "2]/form/div/div[2]/div/ol/li[2]/div["
                        "2]/table/tbody/tr/td/span[2]/table/tbody/tr["
                        "1]/td/div/span/div[2]/table[3]/tbody/tr/td[28]"
                    )
                    insert_html.click()
                except ElementNotInteractableException:
                    self.driver.find_element_by_id(
                        "messagetext_bb_slidercontrol"
                    ).click()
                    sleep(0.2)
                    insert_html = self.driver.find_element_by_xpath(
                        "/html/body/div[5]/div[2]/div/div/div/div/div["
                        "2]/form/div/div[2]/div/ol/li[2]/div["
                        "2]/table/tbody/tr/td/span[2]/table/tbody/tr["
                        "1]/td/div/span/div[2]/table[3]/tbody/tr/td[28]"
                    )
                    insert_html.click()
                self.send_data_output(
                    "Insertando código HTML en ventana emergente")
                old_window = self.driver.window_handles[0]
                new_window = self.driver.window_handles[1]

                self.driver.switch_to.window(new_window)
                html = self.driver.find_element_by_id("htmlSource")
                html.click()
                html.clear()

                relative_path = self.path[: self.path.rindex("/") + 1]

                hmtl_file = open(relative_path + url_txt,
                                 encoding="utf-8", mode="r")

                complete_html_file = hmtl_file.read()
                complete_html_file = complete_html_file.replace("\n", "")

                html.send_keys(complete_html_file)

                insert_btn = self.driver.find_element_by_id("insert")
                insert_btn.click()

                self.driver.switch_to.window(old_window)
            elif post_type == "TEXT":
                self.driver.switch_to.frame("messagetext_ifr")
                body = self.driver.find_element_by_xpath("html/body")
                sleep(1)
                body.send_keys(url_txt)
                self.driver.switch_to.default_content()
            if send_immediately == "Y":
                self.send_data_output("Marcando envío inmediato")
                box = self.driver.find_element_by_id("pushNotify_true")
                box.send_keys(Keys.SPACE)

            self.submit_changes("bottom_Submit")

            self.send_data_output("Publicado!")

    def post_tutor_info(self):
        lines = parse(self.path)
        for course_id in lines:

            self.send_data_output(
                "Publicando ficha de tutor {} en curso {}".format(
                    self.username, course_id)
            )

            self.driver.get(self.url_dict["courses"].format(self.env))

            self.change_combo_box_value(
                "courseInfoSearchKeyString", "CourseId")

            self.search_bar("courseInfoSearchText", course_id)

            self.click_text_link(course_id)

            edit_mode = self.driver.find_element_by_id('statusText')

            if edit_mode.get_attribute('innerHTML') == 'DESACTIVADO':
                edit_mode.click()
                sleep(0.5)

            sleep(1)

            menu_puller = self.driver.find_element_by_id('menuPuller')

            if menu_puller.get_attribute('title') == 'Mostrar menú Curso':
                menu_puller.click()
                sleep(0.5)

            plus = self.driver.find_element_by_id('addCmItem')
            plus.click()

            sleep(1)

            content_item = self.driver.find_element_by_id(
                'addContentAreaButton')
            content_item.send_keys(Keys.ENTER)

            content_name = self.driver.find_element_by_id('addContentAreaName')
            content_name.send_keys("Contacto Tutoría")

            content_availabilty = self.driver.find_element_by_id(
                'content_area_availability_ckbox')
            content_availabilty.send_keys(Keys.SPACE)

            try:
                submit = self.driver.find_element_by_id('addContentAreaFormSubmit')
                submit.send_keys(Keys.ENTER)
                self.driver.find_element_by_link_text('Contacto Tutoría').click()
            except ElementClickInterceptedException:
                self.driver.find_element_by_id('addContentAreaFormCancel').click()
                self.driver.find_element_by_link_text('Contacto Tutoría').click()

            self.driver.find_element_by_xpath(
                '/html/body/div[5]/div[2]/div/div/div/div/div[1]/div/span[1]/a').click()

            text_only = self.driver.find_element_by_xpath('/html/body/div[7]/ul/li[5]/a')

            if text_only.get_attribute('title') == 'Mostrar solo texto':
                self.driver.get(text_only.get_attribute('href'))

            add_element = self.driver.find_element_by_id(
                'content-handler-resource/x-bb-document')
            self.driver.get(add_element.get_attribute('href'))

            elem_title = self.driver.find_element_by_id("user_title")
            elem_title.send_keys('Contacto Tutoría')

            self.driver.execute_script("window.scrollTo(0, 300)")

            sleep(3)

            try:
                insert_image = self.driver.find_element_by_xpath(
                    "/html/body/div[5]/div[2]/div/div/div/div/div["
                    "2]/form/div/div[2]/div/ol/li[3]/div["
                    "2]/table/tbody/tr/td/span[2]/table/tbody/tr["
                    "1]/td/div/span/div[2]/table[3]/tbody/tr/td[4]"
                )
                insert_image.click()
            except ElementNotInteractableException:
                self.driver.find_element_by_id(
                    "messagetext_bb_slidercontrol"
                ).click()
                sleep(0.2)
                insert_image = self.driver.find_element_by_xpath(
                    "/html/body/div[5]/div[2]/div/div/div/div/div["
                    "2]/form/div/div[2]/div/ol/li[3]/div["
                    "2]/table/tbody/tr/td/span[2]/table/tbody/tr["
                    "1]/td/div/span/div[2]/table[3]/tbody/tr/td[4]"
                )
                insert_image.click()
            finally:
                self.send_data_output(
                    "Adjuntando URL de IMG en ventana emergente")
                old_window = self.driver.window_handles[0]
                new_window = self.driver.window_handles[1]

                self.driver.switch_to.window(new_window)
                img_text = self.driver.find_element_by_id(
                    "imagepackage_selectedCSFilePath"
                )
                img_text.send_keys(self.url_dict['tutor_info'])

                alt = self.driver.find_element_by_id("alt")
                alt.send_keys(".")

                title = self.driver.find_element_by_id("title")
                title.send_keys(".")

                insert_btn = self.driver.find_element_by_id("insert")
                insert_btn.click()

                self.driver.switch_to.window(old_window)

            self.submit_changes('bottom_Submit')

            self.send_data_output('Publicada!')

            sleep(1)


if __name__ == "__main__":
    FILE = "prueba.txt"
    thing = BbScripts("usuario186", "123456", func=5, path=FILE)
    # thing.change_role("test.txt")
    # thing.disable_students(file)
