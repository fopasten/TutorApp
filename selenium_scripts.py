from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException, ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from fileparser import parse


class BbScripts:
    def __init__(self, username, password, func=None, path=None, logger=None, output=None, env=None):
        try:
            chrome_options = Options()
            prefs = {"profile.managed_default_content_settings.images": 2}
            chrome_options.add_experimental_option("prefs", prefs)
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

            self.func_dict = {1: self.change_role,
                              2: self.disable_students,
                              3: self.change_date,
                              4: self.post_announcements,
                              5: self.disable_students_av}

            self.send_data_output("Entrando con credenciales proporcionadas")

            self.login()

            self.send_data_output("Ejecutando script")

            self.func_dict[func]()
        except NoSuchWindowException:
            self.send_data_output("Ventana cerrada")
        finally:
            self.driver.close()
            self.driver.quit()

    def __del__(self):
        self.driver.close()
        self.driver.quit()

    def send_data_output(self, text):
        self.logger.info(text)
        self.output(text)
        sleep(0.1)

    def login(self):
        env = "unab"
        self.driver.get("http://{}.blackboard.com".format(env))

        login_btn = self.driver.find_element_by_class_name("boton2")
        login_btn.send_keys(Keys.ENTER)

        login_user = self.driver.find_element_by_id("user_id")
        login_user.send_keys(self.username)

        login_pass = self.driver.find_element_by_id("password")
        login_pass.send_keys(self.password)
        login_pass.send_keys(Keys.ENTER)

    def change_role(self):
        lines = parse(self.path)
        for line in lines:
            course_name = line[0]
            user = line[1]
            role = line[2]

            self.send_data_output("Cambiando rol de {} a {} en el curso {}".format(user, role, course_name))

            self.driver.get("https://unab.blackboard.com/webapps/blackboard/execute/courseManager?sourceType=COURSES")

            course_id_opt = Select(self.driver.find_element_by_id("courseInfoSearchKeyString"))
            course_id_opt.select_by_value("CourseId")

            text_box = self.driver.find_element_by_id("courseInfoSearchText")
            text_box.clear()
            text_box.send_keys(course_name)
            text_box.send_keys(Keys.ENTER)

            course = self.driver.find_element_by_link_text(course_name)
            course.click()

            current = self.driver.current_url
            course_id = current[current.index("course_id="):]

            if "course_id=_1" in course_id:
                course_id = course_id[:course_id.index("_1", course_id.index("_1") + 2) + 2]
            else:
                course_id = course_id[:course_id.index("_1") + 2]
            self.driver.get("https://unab.blackboard.com/webapps/blackboard/execute/userManager?" + course_id)

            search_operator = Select(self.driver.find_element_by_id("userInfoSearchOperatorString"))
            search_operator.select_by_value("Equals")

            user_text = self.driver.find_element_by_id("search_text")
            user_text.clear()
            user_text.send_keys(user)
            user_text.send_keys(Keys.ENTER)

            try:
                usermenu = self.driver.find_element_by_xpath(
                    "/html/body/div[5]/div[2]/div/div/div/div/div[4]"
                    "/form/div[2]/div[3]/div/table/tbody/tr/th/span[2]/a")

            except NoSuchElementException:
                usermenu = self.driver.find_element_by_xpath(
                    "/html/body/div[5]/div[2]/div/div/div/div/div[3]"
                    "/form/div[2]/div[3]/div/table/tbody/tr/th/span[2]/a")

            usermenu.click()

            modify_role = self.driver.find_element_by_id("cp_course_role_modify")
            modify_role.click()

            role = self.driver.find_element_by_id(role)
            role.send_keys(Keys.NULL)
            role.click()

            save = self.driver.find_element_by_id("bottom_Submit")
            save.click()

            self.send_data_output("Completado con éxito")

    def disable_students(self):
        lines = parse(self.path)
        for course_name in lines:
            self.send_data_output("Procesando {}".format(course_name))
            nrc = course_name[course_name.index("_") + 1:course_name.index("_", course_name.index("_") + 1)]
            term = course_name[:course_name.index("_")]

            user_list = []
            user_listbb = []

            self.driver.get(
                "http://ssb.unab.cl:9027/pls/PROD/bwwreplistados_cursos.lista_curso3?" +
                "periodo={}&".format(term) +
                "nrc={}&".format(nrc) +
                "cod_actividad=TEO")

            try:
                n = 5
                while True:

                    table_id = self.driver.find_element_by_xpath('/html/body/table[{0}]'.format(n))
                    rows = table_id.find_elements_by_tag_name('tr')

                    for row in rows:
                        col = row.find_elements_by_tag_name('td')
                        username = col[3]
                        user_list.append(username.text)
                    n += 5
            except NoSuchElementException:
                pass

            self.send_data_output("Se han encontrado {} estudiantes en la lista de Banner".format(len(user_list)))

            self.driver.get(
                "https://unab.blackboard.com/webapps/blackboard/execute/courseManager?sourceType=COURSES")

            course_id_opt = Select(self.driver.find_element_by_id("courseInfoSearchKeyString"))
            course_id_opt.select_by_value("CourseId")

            text_box = self.driver.find_element_by_id("courseInfoSearchText")
            text_box.clear()
            text_box.send_keys(course_name)
            text_box.send_keys(Keys.ENTER)

            course = self.driver.find_element_by_link_text(course_name)
            course.click()

            current = self.driver.current_url
            course_id = current[current.index("course_id="):]

            if "course_id=_1" in course_id:
                course_id = course_id[:course_id.index("_1", course_id.index("_1") + 2) + 2]
            else:
                course_id = course_id[:course_id.index("_1") + 2]

            self.driver.get(
                "https://unab.blackboard.com/webapps/blackboard/execute/userManager?{}".format(course_id))

            try:
                show_all = self.driver.find_element_by_id('listContainer_showAllButton')
                show_all.send_keys(Keys.ENTER)
            except NoSuchElementException:
                pass

            table_id = self.driver.find_element_by_id("listContainer_databody")
            rows = table_id.find_elements_by_tag_name("tr")

            for row in rows:
                col1 = row.find_element_by_tag_name('th')
                col1 = col1.find_element_by_tag_name('span')
                col5 = row.find_elements_by_tag_name('td')[4]
                col5 = col5.find_elements_by_tag_name('span')[1]
                username = col1.text
                if "Student" in col5.text or "Estudiante" in col5.text:
                    if "_preview" not in username:
                        username = str(col1.text).strip()
                        user_listbb.append(username)

            self.send_data_output("Se han encontrado {} estudiantes en la lista de Blackboard".format(len(user_listbb)))

            list_difference = [item for item in user_listbb if item not in user_list]

            self.send_data_output("Ajustando diferencia de {} estudiantes en Blackboard".format(len(list_difference)))

            for user in list_difference:
                self.driver.get("https://unab.blackboard.com/webapps/blackboard/execute/userManager?" + course_id)

                search_operator = Select(self.driver.find_element_by_id("userInfoSearchOperatorString"))
                search_operator.select_by_value("Equals")

                user_text = self.driver.find_element_by_id("search_text")
                user_text.clear()
                user_text.send_keys(user)
                user_text.send_keys(Keys.ENTER)

                try:
                    usermenu = self.driver.find_element_by_xpath(
                        "/html/body/div[5]/div[2]/div/div/div/div/div[4]"
                        "/form/div[2]/div[3]/div/table/tbody/tr/th/span[2]/a")

                except NoSuchElementException:
                    usermenu = self.driver.find_element_by_xpath(
                        "/html/body/div[5]/div[2]/div/div/div/div/div[3]"
                        "/form/div[2]/div[3]/div/table/tbody/tr/th/span[2]/a")

                usermenu.click()

                modify_role = self.driver.find_element_by_id("cp_course_availability")
                modify_role.click()

                available = Select(self.driver.find_element_by_id("availableIndex"))
                available.select_by_value("false")

                save = self.driver.find_element_by_id("bottom_Submit")
                save.click()

            search_operator = Select(self.driver.find_element_by_id("userInfoSearchOperatorString"))
            search_operator.select_by_value("NotBlank")

            user_text = self.driver.find_element_by_id("search_text")
            user_text.clear()
            user_text.send_keys(Keys.ENTER)
            self.send_data_output("Curso {} completado, {} usuarios deshabilitados:\n".format(
                course_name, len(list_difference))
                                  + ("{}\n" * len(list_difference)).format(*list_difference))

    def change_date(self):
        properties = "https://unab.blackboard.com/webapps/blackboard/execute/cp/courseProperties?" \
                     "dispatch=editProperties&family=cp_edit_properties&{}"
        lines = parse(self.path)
        for elem in lines:
            course_name = elem[0]
            if len(course_name) == 1:
                return
            value = elem[1]

            self.driver.get(
                "https://unab.blackboard.com/webapps/blackboard/execute/courseManager?sourceType=COURSES")

            course_id_opt = Select(self.driver.find_element_by_id("courseInfoSearchKeyString"))
            course_id_opt.select_by_value("CourseId")

            text_box = self.driver.find_element_by_id("courseInfoSearchText")
            text_box.clear()
            text_box.send_keys(course_name)
            text_box.send_keys(Keys.ENTER)

            course = self.driver.find_element_by_link_text(course_name)
            course.click()

            current = self.driver.current_url
            course_id = current[current.index("course_id="):]

            if "course_id=_1" in course_id:
                course_id = course_id[:course_id.index("_1", course_id.index("_1") + 2) + 2]
            else:
                course_id = course_id[:course_id.index("_1") + 2]

            self.driver.get(properties.format(course_id))

            end_date_chk = self.driver.find_element_by_id("end_duration")
            end_date_chk.send_keys(Keys.NULL)  # Focus

            if value == "Y":
                if not end_date_chk.is_selected():
                    end_date_chk.send_keys(Keys.SPACE)
            elif value == "N":
                if end_date_chk.is_selected():
                    end_date_chk.send_keys(Keys.SPACE)

            save = self.driver.find_element_by_id("bottom_Submit")
            save.click()

            self.send_data_output("Completado, curso {} fue marcado con {} en el cierre".format(course_name, value))

    def post_announcements(self):
        lines = parse(self.path)
        for elem in lines:
            course_name = elem[0]
            post_type = elem[1]
            subject = elem[2]
            url_txt = elem[3]
            send_immediately = elem[4]

            self.send_data_output("Procesando anuncio tipo {} en {}".format(post_type, course_name))

            self.driver.get(
                "https://unab.blackboard.com/webapps/blackboard/execute/courseManager?sourceType=COURSES")

            course_id_opt = Select(self.driver.find_element_by_id("courseInfoSearchKeyString"))
            course_id_opt.select_by_value("CourseId")

            text_box = self.driver.find_element_by_id("courseInfoSearchText")
            text_box.clear()
            text_box.send_keys(course_name)
            text_box.send_keys(Keys.ENTER)

            course = self.driver.find_element_by_link_text(course_name)
            course.click()

            current = self.driver.current_url
            course_id = current[current.index("course_id="):]

            if "course_id=_1" in course_id:
                course_id = course_id[:course_id.index("_1", course_id.index("_1") + 2) + 2]
            else:
                course_id = course_id[:course_id.index("_1") + 2]

            self.driver.get("https://unab.blackboard.com/webapps/blackboard/execute/announcement?"
                            "method=search&editMode=true&viewChoice=2&{}&"
                            "context=course&internalHandle=cp_announcements".format(course_id))

            course_id2 = course_id.split("=")
            course_id2 = course_id2[1]

            self.driver.execute_script("javascript:designer_participant.toggleEditMode('javascript:"
                                       "Announcement.addAnnouncement()','{}','designer')".format(course_id2))

            subj = self.driver.find_element_by_id("subject")
            subj.send_keys(subject)

            self.driver.find_element_by_id("isPermanent_true").send_keys(Keys.NULL)

            sleep(3)

            if post_type == "IMG":
                try:
                    insert_image = self.driver.find_element_by_xpath("/html/body/div[5]/div[2]/div/div/div/div/div["
                                                                     "2]/form/div/div[2]/div/ol/li[2]/div["
                                                                     "2]/table/tbody/tr/td/span[2]/table/tbody/tr["
                                                                     "1]/td/div/span/div[2]/table[3]/tbody/tr/td[4]")
                    insert_image.click()
                except ElementNotInteractableException:
                    self.driver.find_element_by_id("messagetext_bb_slidercontrol").click()
                    sleep(0.2)
                    insert_image = self.driver.find_element_by_xpath("/html/body/div[5]/div[2]/div/div/div/div/div["
                                                                     "2]/form/div/div[2]/div/ol/li[2]/div["
                                                                     "2]/table/tbody/tr/td/span[2]/table/tbody/tr["
                                                                     "1]/td/div/span/div[2]/table[3]/tbody/tr/td[4]")
                    insert_image.click()
                finally:
                    self.send_data_output("Adjuntando URL de IMG en ventana emergente")
                    old_window = self.driver.window_handles[0]
                    new_window = self.driver.window_handles[1]

                    self.driver.switch_to.window(new_window)
                    img_text = self.driver.find_element_by_id("imagepackage_selectedCSFilePath")
                    img_text.send_keys(url_txt)

                    alt = self.driver.find_element_by_id("alt")
                    alt.send_keys(".")

                    title = self.driver.find_element_by_id("title")
                    title.send_keys(".")

                    insert_btn = self.driver.find_element_by_id("insert")
                    insert_btn.click()

                    self.driver.switch_to.window(old_window)
            elif post_type == "TEXT":
                self.driver.switch_to.frame("messagetext_ifr")
                body = self.driver.find_element_by_xpath('html/body')
                sleep(1)
                body.send_keys(url_txt)
                self.driver.switch_to.default_content()
            if send_immediately == "Y":
                self.send_data_output("Marcando envío inmediato")
                box = self.driver.find_element_by_id("pushNotify_true")
                box.send_keys(Keys.SPACE)

            submit = self.driver.find_element_by_id("bottom_Submit")
            submit.click()

            self.send_data_output("Publicado!")

    def disable_students_av(self):
        lines = parse(self.path)
        for course_name in lines:
            self.send_data_output("Procesando {}".format(course_name))
            term = course_name[course_name.index(".") + 1:]
            nrc = term[term.index(".") + 1:]
            nrc = nrc[:nrc.index(".")]
            term = term[:term.index(".")]

            user_list = []
            user_listbb = []

            self.driver.get(
                "http://ssb.unab.cl:9027/pls/PROD/bwwreplistados_cursos.lista_curso3?" +
                "periodo={}&".format(term) +
                "nrc={}&".format(nrc) +
                "cod_actividad=TEO")

            try:
                n = 5
                while True:

                    table_id = self.driver.find_element_by_xpath('/html/body/table[{0}]'.format(n))
                    rows = table_id.find_elements_by_tag_name('tr')

                    for row in rows:
                        col = row.find_elements_by_tag_name('td')
                        username = col[3]
                        user_list.append(username.text)
                    n += 5
            except NoSuchElementException:
                pass

            self.send_data_output("Se han encontrado {} estudiantes en la lista de Banner".format(len(user_list)))

            self.driver.get(
                "https://unab.blackboard.com/webapps/blackboard/execute/courseManager?sourceType=COURSES")

            course_id_opt = Select(self.driver.find_element_by_id("courseInfoSearchKeyString"))
            course_id_opt.select_by_value("CourseId")

            text_box = self.driver.find_element_by_id("courseInfoSearchText")
            text_box.clear()
            text_box.send_keys(course_name)
            text_box.send_keys(Keys.ENTER)

            course = self.driver.find_element_by_link_text(course_name)
            course.click()

            current = self.driver.current_url
            course_id = current[current.index("course_id="):]

            if "course_id=_1" in course_id:
                course_id = course_id[:course_id.index("_1", course_id.index("_1") + 2) + 2]
            else:
                course_id = course_id[:course_id.index("_1") + 2]

            self.driver.get(
                "https://unab.blackboard.com/webapps/blackboard/execute/userManager?{}".format(course_id))

            try:
                show_all = self.driver.find_element_by_id('listContainer_showAllButton')
                show_all.send_keys(Keys.ENTER)
            except NoSuchElementException:
                pass

            table_id = self.driver.find_element_by_id("listContainer_databody")
            rows = table_id.find_elements_by_tag_name("tr")

            for row in rows:
                col1 = row.find_element_by_tag_name('th')
                col1 = col1.find_element_by_tag_name('span')
                col5 = row.find_elements_by_tag_name('td')[4]
                col5 = col5.find_elements_by_tag_name('span')[1]
                username = col1.text
                if "Student" in col5.text or "Estudiante" in col5.text:
                    if "_preview" not in username:
                        username = str(col1.text).strip()
                        user_listbb.append(username)

            self.send_data_output(
                "Se han encontrado {} estudiantes en la lista de Blackboard".format(len(user_listbb)))

            list_difference = [item for item in user_listbb if item not in user_list]

            self.send_data_output(
                "Ajustando diferencia de {} estudiantes en Blackboard".format(len(list_difference)))

            for user in list_difference:
                self.driver.get("https://unab.blackboard.com/webapps/blackboard/execute/userManager?" + course_id)

                search_operator = Select(self.driver.find_element_by_id("userInfoSearchOperatorString"))
                search_operator.select_by_value("Equals")

                user_text = self.driver.find_element_by_id("search_text")
                user_text.clear()
                user_text.send_keys(user)
                user_text.send_keys(Keys.ENTER)

                try:
                    usermenu = self.driver.find_element_by_xpath(
                        "/html/body/div[5]/div[2]/div/div/div/div/div[4]"
                        "/form/div[2]/div[3]/div/table/tbody/tr/th/span[2]/a")

                except NoSuchElementException:
                    usermenu = self.driver.find_element_by_xpath(
                        "/html/body/div[5]/div[2]/div/div/div/div/div[3]"
                        "/form/div[2]/div[3]/div/table/tbody/tr/th/span[2]/a")

                usermenu.click()

                modify_role = self.driver.find_element_by_id("cp_course_availability")
                modify_role.click()

                available = Select(self.driver.find_element_by_id("availableIndex"))
                available.select_by_value("false")

                save = self.driver.find_element_by_id("bottom_Submit")
                save.click()

            search_operator = Select(self.driver.find_element_by_id("userInfoSearchOperatorString"))
            search_operator.select_by_value("NotBlank")

            user_text = self.driver.find_element_by_id("search_text")
            user_text.clear()
            user_text.send_keys(Keys.ENTER)
            self.send_data_output("Curso {} completado, {} usuarios deshabilitados:\n".format(
                course_name, len(list_difference))
                                  + ("{}\n" * len(list_difference)).format(*list_difference))


if __name__ == '__main__':
    file = 'test_anuncios.txt'
    thing = BbScripts("usuario186", "123456", func=4, path=file)
    # thing.change_role("test.txt")
    # thing.disable_students(file)
