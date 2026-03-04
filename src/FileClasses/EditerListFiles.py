class EditerListFiles:
    """
    Класс для манипуляций со списком файлов:
    - Удаление файлов
    - Добавление файлов
    """

    def __init__(self, filesList: set[str]) -> None:
        self.filesList = filesList

    def doDeleteFile(self, file_name) -> None:
        if file_name in self.filesList:
            self.filesList.remove(file_name)

    def doAddFile(self, file_name) -> None:
        self.filesList.add(file_name)

    def useBlackList(self, black_list) -> None:
        """
        Функция для удаления из нашего списка всех файлов, которые входят в черный список.
        :param black_list: Наш черный список
        :return:
        """
        for i in black_list:
            self.doDeleteFile(i)

    def getFilesList(self) -> set[str]:
        return self.filesList
